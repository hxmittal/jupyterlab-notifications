/// <reference types="react" />
import { ReactWidget } from "@jupyterlab/apputils";
export declare function systemNotification(notification: any): void;
export declare function NotificationCenter(props: any): JSX.Element;
export declare function notifyInCenter(notification: any): void;
export declare class notificationWidget extends ReactWidget {
    constructor();
    render(): JSX.Element;
}
