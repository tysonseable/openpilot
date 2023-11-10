#pragma once

#include <QPainter>
#include <QPushButton>
#include <thread>
#include <chrono>
#include <memory>
#include <cstdint>
#include <algorithm>
#include <time.h>
#include <sys/time.h>
#include "omx_encoder.h"
#include "blocking_queue.h"
#include "libyuv.h"
#include "selfdrive/ui/ui.h"

class ScreenRecorder : public QPushButton {
  Q_OBJECT

public:
  explicit ScreenRecorder(QWidget* parent = nullptr);
  ~ScreenRecorder() override;
  void update_screen();
  void toggle();

public slots:
  void btnReleased();
  void btnPressed();

protected:
  void paintEvent(QPaintEvent* event) override;

private:
  bool recording = false;
  long long started = 0;
  int src_width = 2160, src_height = 1080;
  int dst_width, dst_height;
  QColor recording_color;
  int frame = 0;
  std::unique_ptr<OmxEncoder> encoder;
  std::unique_ptr<uint8_t[]> rgb_buffer;
  std::unique_ptr<uint8_t[]> rgb_scale_buffer;
  std::thread encoding_thread;
  BlockingQueue<QImage> image_queue;
  QWidget* rootWidget;

  void applyColor();
  void openEncoder(const char* filename);
  void closeEncoder();
  void encoding_thread_func();
  void initializeEncoder();
  void start();
  void stop();
};
