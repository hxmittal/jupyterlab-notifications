import React from "react";
import Button from "@material-ui/core/Button";
import Snackbar from "@material-ui/core/Snackbar";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";
export default function SimpleSnackbar() {
    const [open, setOpen] = React.useState(false);
    const handleClose = () => {
        setOpen(false);
    };
    setOpen(true);
    return (React.createElement("div", null,
        React.createElement(Snackbar, { anchorOrigin: {
                vertical: "bottom",
                horizontal: "left",
            }, open: open, autoHideDuration: 6000, onClose: handleClose, message: "Note archived", action: React.createElement(React.Fragment, null,
                React.createElement(Button, { color: "secondary", size: "small", onClick: handleClose }, "UNDO"),
                React.createElement(IconButton, { size: "small", "aria-label": "close", color: "inherit", onClick: handleClose },
                    React.createElement(CloseIcon, { fontSize: "small" }))) })));
}
//# sourceMappingURL=snackbar.js.map