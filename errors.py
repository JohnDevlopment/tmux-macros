from __future__ import annotations

import errno

from my_typings import StrPath


class OSErrorFactory:
    """
    Singleton that constructs OSError-derived exceptions.

    Each static method constructs an exception with the
    appropriate arguments.
    """

    @staticmethod
    def FileNotFoundError(file1: StrPath, file2: StrPath | None = None):
        """
        Construct a FileNotFoundError.

        FILE1 is the name of the file that caused the exception
        (i.e., the filename passed to the calling function). If
        FILE2 is provided, it represents the second filename passed
        to the calling function (for example, os.rename()).
        """
        file1 = str(file1)
        if file2:
            return FileNotFoundError(
                errno.ENOENT, errno.errorcode[errno.ENOENT], file1, str(file2)
            )
        return FileNotFoundError(errno.ENOENT, errno.errorcode[errno.ENOENT], file1)

    @staticmethod
    def FileExistsError(file1: StrPath):
        """
        Construct a FileExistsError.

        FILE1 is the name of the file that caused the exception
        (i.e., the filename passed to the calling function).
        """
        file1 = str(file1)
        return FileExistsError(errno.EEXIST, errno.errorcode[errno.EEXIST], file1)

    @staticmethod
    def NotADirectoryError(pth: StrPath):
        """
        Construct a NotADirectoryError.

        PTH is the path for which the error was generated.
        """
        return NotADirectoryError(
            errno.ENOTDIR, errno.errorcode[errno.ENOTDIR], str(pth)
        )
