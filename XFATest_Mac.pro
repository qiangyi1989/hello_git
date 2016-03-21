#-------------------------------------------------
#
# Project created by QtCreator 2015-11-20T11:23:43
#
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = XFATest
TEMPLATE = app

DEFINES += _FXQA_PDFIUM_ PDF_ENABLE_V8 _FXQA_PLATFORM_QT_ PNG_PREFIX \
PNGPREFIX_H \
PDF_ENABLE_V8 \
PDF_ENABLE_XFA \
PNG_USE_READ_MACROS \
V8_DEPRECATION_WARNINGS \
NOMINMAX \
_FXQA_PLATFORM_QT_

LIBS += -stdlib=libc++

QMAKE_CXXFLAGS += -stdlib=libc++
QMAKE_CXXFLAGS += -std=c++11
#QMAKE_CXXFLAGS += -mmacosx-version-min=10.7
QMAKE_LFLAGS += -mmacosx-version-min=10.7

# If OSX 10.10
#QMAKE_MACOSX_DEPLOYMENT_TARGENT = 10.7

LIBS += -framework AppKit
LIBS += -framework CoreAudio
LIBS += -framework AudioToolbox

LIBS += \
./XFA/lib/libfxqapdfium.a \
 -ldl

INCLUDEPATH += XFA \
    XFA/core/include \
    XFA/public \
    XFA/xfa \
    XFA/fpdfsdk \
    XFA/xfa/src \
    XFA/xfa/src/fgas/include \
    XFA/xfa/include \
    XFA/xfa/src/fdp/include \
    XFA/xfa/include/fxgraphics \
    XFA/xfa/src/fee/include \
    XFA/xfa/include/fwl \
    XFA/xfa/include/fxjse \
    XFA/xfa/include/fxfa \
    XFA/v8 \
    XFA/fpdfsdk/include

SOURCES += src/main.cpp\
    src/fxqa_charset.cpp \
    src/FXQA_ViewItem.cpp \
    src/FXQA_XFAManager.cpp \
    src/xfatest.cpp

HEADERS  += \
    src/fxqa_charset.h \
    src/FXQA_ViewItem.h \
    src/FXQA_XFAManager.h \
    src/xfatest.h

FORMS    += \
    src/xfatest.ui
