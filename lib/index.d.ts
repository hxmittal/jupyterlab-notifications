import { JupyterFrontEndPlugin } from "@jupyterlab/application";
import "bootstrap/dist/css/bootstrap.min.css";
import "react-toastify/dist/ReactToastify.css";
import "../style/main.css";
/**
 * Initialization data for the jupyterlab-todo extension.
 */
declare const plugin: JupyterFrontEndPlugin<void>;
export default plugin;
