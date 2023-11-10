#include "selfdrive/ui/qt/widgets/slider.h"

#include "selfdrive/ui/qt/offroad/settings.h"


CustomSlider::CustomSlider(const std::string &param, 
                           CerealSetterFunction cerealSetFunc, 
                           const QString &unit,
                           const QString &title, 
                           double paramMin, 
                           double paramMax, 
                           double defaultVal, 
                           QWidget *parent) // Define the constructor
                          : // Call the base class constructor
                          QSlider(Qt::Horizontal, parent),
                          param(param), title(title), unit(unit),
                          paramMin(paramMin), paramMax(paramMax), defaultVal(defaultVal),
                          cerealSetFunc(cerealSetFunc) // Initialize the setter function
                          {
                            initialize(); // Call the initialize function
                          } // End of constructor

void CustomSlider::initialize()
{
  // Create UI elements
  sliderItem = new QWidget(parentWidget()); // Create a new widget
  // Create a vertical layout to stack the title and reset button on top of the slider
  QVBoxLayout *mainLayout = new QVBoxLayout(sliderItem); 
  // Create a horizontal layout to put the title and reset on left and right respectively
  QHBoxLayout *titleLayout = new QHBoxLayout();
  mainLayout->addLayout(titleLayout);

  // Create the title label
  label = new QLabel(title);
  label->setStyleSheet(LabelStyle);
  label->setTextFormat(Qt::RichText);
  titleLayout->addWidget(label, 0, Qt::AlignLeft);

  // Create the reset button
  resetButton = new ButtonControl("  ", tr("RESET"));
  titleLayout->addWidget(resetButton, 0, Qt::AlignRight);
  
  
  // slider settings
  setFixedHeight(100);
  setMinimum(sliderMin);
  setMaximum(sliderMax);
  setStyleSheet(SliderStyle);
  label->setStyleSheet(LabelStyle);
  
  double value;
  if (Params().getBool("BehaviordInitialized")){
    QString valueStr = QString::fromStdString(Params().get(param));
    value = QString(valueStr).toDouble();
  } else{
    value = defaultVal;
  }

  // Set the value of the param in the behavior struct
  MessageBuilder msg;
  auto behavior = msg.initEvent().initBehavior();
  cerealSetFunc(behavior, value);

  setupConnections();
  // Set the slider value
  setSliderValue(value);

  mainLayout->addWidget(this);
}

void CustomSlider::setSliderValue(double value) {
  setValue(sliderMin + (value - paramMin) / (paramMax - paramMin) * (sliderRange));
}

void CustomSlider::setupConnections() {
  // Value Changed
  connect(this, &CustomSlider::valueChanged, [=](int value) {
    double dValue = paramMin + (paramMax - paramMin) * (value - sliderMin) / (sliderRange);
    updateLabel(dValue);
  });
  
  // Release slider
  connect(this, &CustomSlider::sliderReleased, [this]() {
    emit sliderValueChanged();
  });
  // Connect the reset button to set the slider value to the default value
  connect(resetButton, &ButtonControl::clicked, [&]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to reset ") + QString::fromStdString(param) + "?", tr("Reset"), this)) {
      this->setValue(sliderMin + (defaultVal - paramMin) / (paramMax - paramMin) * (sliderRange));
      emit this->sliderValueChanged();
    }
  });
}

void CustomSlider::updateLabel(double value) {
  label->setText(title + " " + QString::number(value, 'f', 2) + " " + unit);
}
