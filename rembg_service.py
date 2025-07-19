import logging
from pathlib import Path
from typing import Tuple

import aiofiles
from rembg import remove, new_session

from settings import Settings

logger = logging.getLogger(__name__)
_session = new_session() 

async def remove_bg(source: Path, dest: Path) -> Path:
    """Return path to PNG with background removed."""
    async with aiofiles.open(source, "rb") as f:
        data_in = await f.read()

    data_out = remove(data_in, session=_session)

    async with aiofiles.open(dest, mode="wb") as f:
        await f.write(data_out)

    logger.info("Background removed → %s", dest.name)
    return dest