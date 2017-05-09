from PyQt5.QtCore import pyqtSlot

from urh.ContinuousSceneManager import ContinuousSceneManager
from urh.controller.SendDialogController import SendDialogController
from urh.controller.SendRecvDialogController import SendRecvDialogController
from urh.dev.VirtualDevice import VirtualDevice, Mode
from urh.signalprocessing.ContinuousModulator import ContinuousModulator


class ContinuousSendDialogController(SendDialogController):
    def __init__(self, project_manager, messages, modulators, total_samples:int, parent, testing_mode=False):
        super().__init__(project_manager, modulated_data=None, parent=parent, testing_mode=testing_mode)
        self.messages = messages
        self.modulators = modulators

        self.graphics_view = self.ui.graphicsViewContinuousSend
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_continuous_send)

        self.total_samples = total_samples
        self.ui.progressBar.setMaximum(total_samples)

        self.continuous_modulator = ContinuousModulator(messages, modulators)
        self.scene_manager = ContinuousSceneManager(ring_buffer=self.continuous_modulator.ring_buffer, parent=self)
        self.scene_manager.init_scene()
        self.graphics_view.setScene(self.scene_manager.scene)

        self.setWindowTitle("Send data (continuous mode)")

        self.init_device()

        self.create_connects()

    def create_connects(self):
        SendRecvDialogController.create_connects(self)

    def _update_send_indicator(self, width: int):
        pass

    def update_view(self):
        super().update_view()
        self.scene_manager.init_scene()
        self.scene_manager.show_full_scene()
        self.graphics_view.update()

    @pyqtSlot()
    def on_device_started(self):
        self.continuous_modulator.start()
        super().on_device_started()

    @pyqtSlot()
    def on_device_stopped(self):
        self.continuous_modulator.stop()
        super().on_device_stopped()

    def init_device(self):
        device_name = self.ui.cbDevice.currentText()
        num_repeats = self.ui.spinBoxNRepeat.value()

        self.device = VirtualDevice(self.backend_handler, device_name, Mode.send,
                                    device_ip="192.168.10.2", sending_repeats=num_repeats, parent=self)
        self.ui.btnStart.setEnabled(True)

        try:
            self.device.is_send_continuous = True
            self.device.continuous_send_ring_buffer = self.continuous_modulator.ring_buffer
            self.device.total_samples_to_send = self.total_samples

            self._create_device_connects()
        except ValueError as e:
            self.ui.txtEditErrors.setText("<font color='red'>" + str(e) + "<font>")
            self.ui.btnStart.setEnabled(False)