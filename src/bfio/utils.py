import scyjava
import logging
try:

    def start() -> str:
        """Start the jvm.

        This function starts the jvm and imports all the necessary Java classes
        to read images using the Bio-Formats toolbox.

        Return:
            The Bio-Formats JAR version.
        """

        global JAR_VERSION
        scyjava.config.endpoints.append("ome:formats-gpl:7.2.0")
        scyjava.start_jvm()
        import loci

        loci.common.DebugTools.setRootLevel("ERROR")
        JAR_VERSION = loci.formats.FormatTools.VERSION

        logging.getLogger("bfio.start").info(
            "bioformats_package.jar version = {}".format(JAR_VERSION)
        )

        return JAR_VERSION

except ModuleNotFoundError:

    def start():  # NOQA: D103
        raise ModuleNotFoundError("Error importing jpype or a loci_tools.jar class.")