LOCAL_PATH := $(call my-dir)

###################### liboam ######################
include $(CLEAR_VARS)

LOCAL_MODULE := liboam

LOCAL_MODULE_CLASS := STATIC_LIBRARIES
intermediates := $(local-intermediates-dir)

GEN := $(intermediates)/generated
GENSRC :=
GENSRC += $(intermediates)/oam/ftl_oam_convert.c
GENSRC += $(intermediates)/oam/ftl_oam_convert.h
GENSRC += $(intermediates)/oam/ftl_oam_id.h
GENSRC += $(intermediates)/oam/ftl_oam_init.c
GENSRC += $(intermediates)/oam/ftl_oam_init.h

#LOCAL_EXPORT_C_INCLUDE_DIRS := $(intermediates)/oam
#LOCAL_EXPORT_C_INCLUDE_DIRS := $(LOCAL_PATH)
# NOTE: for sname_def.h

#$(GEN): PRIVATE_INPUT_FILE :=
$(GEN): PRIVATE_PATH := $(LOCAL_PATH)
$(GEN): PRIVATE_INTERMEDIATES_DIR := $(intermediates)

$(GEN): PRIVATE_CUSTOM_TOOL = python3 $(PRIVATE_PATH)/BuildSourceFiles.py -f $< -t $(PRIVATE_PATH)/template -p $(PRIVATE_INTERMEDIATES_DIR)
$(GEN): $(LOCAL_PATH)/Sercomm_STANDALONE_TDD_B_DataModel_RAW.xml
	$(transform-generated-source)
	touch $@
# NOTE: have to touch in the end, because wait to mkdir

# TODO: multi target expend for order
$(GENSRC): $(GEN)
#	@echo "GENSRC: $@ <== ($<)"
# NOTE: always triger or no triger, it is no use

LOCAL_GENERATED_SOURCES += $(GENSRC)

#LOCAL_SRC_FILES := $(GENSRC)

LOCAL_C_INCLUDES += $(LOCAL_PATH)
LOCAL_C_INCLUDES += $(intermediates)

include $(BUILD_STATIC_LIBRARY)

###################### datamodel ######################
include $(CLEAR_VARS)

LOCAL_MODULE := liboam

LOCAL_MODULE_CLASS := STATIC_LIBRARIES
intermediates := $(local-intermediates-dir)
LOCAL_MODULE_CLASS :=

LOCAL_ADDITIONAL_DEPENDENCIES := $(intermediates)/oam/ftl_oam_id.h
# FIXME: avoid func.c compile again

LOCAL_MODULE := datamodel

LOCAL_SRC_FILES :=
LOCAL_SRC_FILES += main.c
LOCAL_SRC_FILES += func.c

#LOCAL_C_INCLUDES += $(LOCAL_PATH)
LOCAL_C_INCLUDES += $(intermediates)

LOCAL_STATIC_LIBRARIES := liboam

include $(BUILD_EXECUTABLE)

