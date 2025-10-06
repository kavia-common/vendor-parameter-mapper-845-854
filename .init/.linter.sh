#!/bin/bash
cd /home/kavia/workspace/code-generation/vendor-parameter-mapper-845-854/vendor_parameter_mapping_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

