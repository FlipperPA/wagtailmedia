from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from django.template.loader import render_to_string

from wagtail.admin.compare import ForeignObjectComparison
from wagtail.admin.panels import FieldPanel
from .deprecation import RemovedInWagtailMedia015Warning

from .models import MediaType
from .utils import format_audio_html, format_video_html
from .widgets import AdminAudioChooser, AdminMediaChooser, AdminVideoChooser


if TYPE_CHECKING:
    from .models import AbstractMedia


class MediaChooserPanel(FieldPanel):
    object_type_name = "media"

    def __init__(self, field_name, media_type=None, *args, **kwargs):
        super().__init__(field_name=field_name, *args, **kwargs)

        self.media_type = media_type

        if self.media_type is None:
            warnings.warn(
                (
                    "The `MediaChooserPanel` field panel is deprecated. "
                    "Please use the `FieldPanel()` instead."
                ),
                RemovedInWagtailMedia015Warning,
                stacklevel=2,
            )
        else:
            warnings.warn(
                (
                    "The `MediaChooserPanel` field panel is deprecated. Please use the "
                    "specialised `AudioChooserPanel()` for audio only "
                    "and `VideoChooserPanel()` for video only."
                ),
                RemovedInWagtailMedia015Warning,
                stacklevel=2,
            )

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(media_type=self.media_type)
        return kwargs

    @property
    def _widget_class(self):
        if self.media_type == "audio":
            return AdminAudioChooser
        elif self.media_type == "video":
            return AdminVideoChooser
        return AdminMediaChooser

    def get_form_options(self) -> dict:
        opts = super().get_form_options()
        if "widgets" in opts:
            opts["widgets"][self.field_name] = self._widget_class
        else:
            opts["widgets"] = {self.field_name: self._widget_class}

        return opts


class MediaFieldComparison(ForeignObjectComparison):
    def htmldiff(self) -> str:
        media_item_a, media_item_b = self.get_objects()
        if not all([media_item_a, media_item_b]):
            return ""

        return render_to_string(
            "wagtailmedia/widgets/compare.html",
            {
                "media_item_a": self.render_media_item(media_item_a),
                "media_item_b": self.render_media_item(media_item_b),
            },
        )

    @staticmethod
    def render_media_item(item: AbstractMedia) -> str:
        if item.type == MediaType.AUDIO:
            return format_audio_html(item)
        else:
            return format_video_html(item)
