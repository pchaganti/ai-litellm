#### What this does ####
#    On success, logs events to Promptlayer
import traceback
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

from pydantic import BaseModel

from litellm.caching.caching import DualCache
from litellm.types.integrations.argilla import ArgillaItem
from litellm.types.llms.openai import AllMessageValues, ChatCompletionRequest
from litellm.types.utils import (
    AdapterCompletionStreamWrapper,
    CallTypes,
    LLMResponseTypes,
    ModelResponse,
    ModelResponseStream,
    StandardCallbackDynamicParams,
    StandardLoggingPayload,
)

if TYPE_CHECKING:
    from opentelemetry.trace import Span as _Span

    from litellm.litellm_core_utils.litellm_logging import Logging as LiteLLMLoggingObj
    from litellm.proxy._types import UserAPIKeyAuth
    from litellm.types.mcp import (
        MCPDuringCallRequestObject,
        MCPDuringCallResponseObject,
        MCPPostCallResponseObject,
        MCPPreCallRequestObject,
        MCPPreCallResponseObject,
    )
    from litellm.types.router import PreRoutingHookResponse

    Span = Union[_Span, Any]
else:
    Span = Any
    LiteLLMLoggingObj = Any
    UserAPIKeyAuth = Any
    MCPPostCallResponseObject = Any
    MCPPreCallRequestObject = Any
    MCPPreCallResponseObject = Any
    MCPDuringCallRequestObject = Any
    MCPDuringCallResponseObject = Any
    PreRoutingHookResponse = Any


class CustomLogger:  # https://docs.litellm.ai/docs/observability/custom_callback#callback-class
    # Class variables or attributes
    def __init__(
        self, 
        turn_off_message_logging: bool = False,

        # deprecated param, use `turn_off_message_logging` instead
        message_logging: bool = True,
        **kwargs
    ) -> None:
        """
        Args:
            turn_off_message_logging: bool - if True, the message logging will be turned off. Message and response will be redacted from StandardLoggingPayload.
            message_logging: bool - deprecated param, use `turn_off_message_logging` instead
        """
        self.message_logging = message_logging
        self.turn_off_message_logging = turn_off_message_logging
        pass

    def log_pre_api_call(self, model, messages, kwargs):
        pass

    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        pass

    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        pass

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        pass

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        pass

    #### ASYNC ####

    async def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        pass

    async def async_log_pre_api_call(self, model, messages, kwargs):
        pass

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        pass

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        pass

    #### PROMPT MANAGEMENT HOOKS ####

    async def async_get_chat_completion_prompt(
        self,
        model: str,
        messages: List[AllMessageValues],
        non_default_params: dict,
        prompt_id: Optional[str],
        prompt_variables: Optional[dict],
        dynamic_callback_params: StandardCallbackDynamicParams,
        litellm_logging_obj: LiteLLMLoggingObj,
        tools: Optional[List[Dict]] = None,
        prompt_label: Optional[str] = None,
        prompt_version: Optional[int] = None,
    ) -> Tuple[str, List[AllMessageValues], dict]:
        """
        Returns:
        - model: str - the model to use (can be pulled from prompt management tool)
        - messages: List[AllMessageValues] - the messages to use (can be pulled from prompt management tool)
        - non_default_params: dict - update with any optional params (e.g. temperature, max_tokens, etc.) to use (can be pulled from prompt management tool)
        """
        return model, messages, non_default_params

    def get_chat_completion_prompt(
        self,
        model: str,
        messages: List[AllMessageValues],
        non_default_params: dict,
        prompt_id: Optional[str],
        prompt_variables: Optional[dict],
        dynamic_callback_params: StandardCallbackDynamicParams,
        prompt_label: Optional[str] = None,
        prompt_version: Optional[int] = None,
    ) -> Tuple[str, List[AllMessageValues], dict]:
        """
        Returns:
        - model: str - the model to use (can be pulled from prompt management tool)
        - messages: List[AllMessageValues] - the messages to use (can be pulled from prompt management tool)
        - non_default_params: dict - update with any optional params (e.g. temperature, max_tokens, etc.) to use (can be pulled from prompt management tool)
        """
        return model, messages, non_default_params

    #### PRE-CALL CHECKS - router/proxy only ####
    """
    Allows usage-based-routing-v2 to run pre-call rpm checks within the picked deployment's semaphore (concurrency-safe tpm/rpm checks).
    """

    async def async_pre_routing_hook(
        self,
        model: str,
        request_kwargs: Dict,
        messages: Optional[List[Dict[str, str]]] = None,
        input: Optional[Union[str, List]] = None,
        specific_deployment: Optional[bool] = False,
    ) -> Optional[PreRoutingHookResponse]:
        """
        This hook is called before the routing decision is made.

        Used for the litellm auto-router to modify the request before the routing decision is made.
        """
        return None

    async def async_filter_deployments(
        self,
        model: str,
        healthy_deployments: List,
        messages: Optional[List[AllMessageValues]],
        request_kwargs: Optional[dict] = None,
        parent_otel_span: Optional[Span] = None,
    ) -> List[dict]:
        return healthy_deployments

    async def async_pre_call_deployment_hook(
        self, kwargs: Dict[str, Any], call_type: Optional[CallTypes]
    ) -> Optional[dict]:
        """
        Allow modifying the request just before it's sent to the deployment.

        Use this instead of 'async_pre_call_hook' when you need to modify the request AFTER a deployment is selected, but BEFORE the request is sent.

        Used in managed_files.py
        """
        pass

    async def async_pre_call_check(
        self, deployment: dict, parent_otel_span: Optional[Span]
    ) -> Optional[dict]:
        pass

    def pre_call_check(self, deployment: dict) -> Optional[dict]:
        pass

    async def async_post_call_success_deployment_hook(
        self,
        request_data: dict,
        response: LLMResponseTypes,
        call_type: Optional[CallTypes],
    ) -> Optional[LLMResponseTypes]:
        """
        Allow modifying / reviewing the response just after it's received from the deployment.
        """
        pass

    #### Fallback Events - router/proxy only ####
    async def log_model_group_rate_limit_error(
        self, exception: Exception, original_model_group: Optional[str], kwargs: dict
    ):
        pass

    async def log_success_fallback_event(
        self, original_model_group: str, kwargs: dict, original_exception: Exception
    ):
        pass

    async def log_failure_fallback_event(
        self, original_model_group: str, kwargs: dict, original_exception: Exception
    ):
        pass

    #### ADAPTERS #### Allow calling 100+ LLMs in custom format - https://github.com/BerriAI/litellm/pulls

    def translate_completion_input_params(
        self, kwargs
    ) -> Optional[ChatCompletionRequest]:
        """
        Translates the input params, from the provider's native format to the litellm.completion() format.
        """
        pass

    def translate_completion_output_params(
        self, response: ModelResponse
    ) -> Optional[BaseModel]:
        """
        Translates the output params, from the OpenAI format to the custom format.
        """
        pass

    def translate_completion_output_params_streaming(
        self, completion_stream: Any
    ) -> Optional[AdapterCompletionStreamWrapper]:
        """
        Translates the streaming chunk, from the OpenAI format to the custom format.
        """
        pass

    ### DATASET HOOKS #### - currently only used for Argilla

    async def async_dataset_hook(
        self,
        logged_item: ArgillaItem,
        standard_logging_payload: Optional[StandardLoggingPayload],
    ) -> Optional[ArgillaItem]:
        """
        - Decide if the result should be logged to Argilla.
        - Modify the result before logging to Argilla.
        - Return None if the result should not be logged to Argilla.
        """
        raise NotImplementedError("async_dataset_hook not implemented")

    #### CALL HOOKS - proxy only ####
    """
    Control the modify incoming / outgoung data before calling the model
    """

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
            "pass_through_endpoint",
            "rerank",
            "mcp_call",
        ],
    ) -> Optional[
        Union[Exception, str, dict]
    ]:  # raise exception if invalid, return a str for the user to receive - if rejected, or return a modified dictionary for passing into litellm
        pass

    async def async_post_call_failure_hook(
        self,
        request_data: dict,
        original_exception: Exception,
        user_api_key_dict: UserAPIKeyAuth,
        traceback_str: Optional[str] = None,
    ):
        pass

    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response: LLMResponseTypes,
    ) -> Any:
        pass

    async def async_logging_hook(
        self, kwargs: dict, result: Any, call_type: str
    ) -> Tuple[dict, Any]:
        """For masking logged request/response. Return a modified version of the request/result."""
        return kwargs, result

    def logging_hook(
        self, kwargs: dict, result: Any, call_type: str
    ) -> Tuple[dict, Any]:
        """For masking logged request/response. Return a modified version of the request/result."""
        return kwargs, result

    async def async_moderation_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        call_type: Literal[
            "completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
            "responses",
            "mcp_call",
        ],
    ) -> Any:
        pass

    async def async_post_call_streaming_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        response: str,
    ) -> Any:
        pass

    async def async_post_call_streaming_iterator_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        response: Any,
        request_data: dict,
    ) -> AsyncGenerator[ModelResponseStream, None]:
        async for item in response:
            yield item

    #### SINGLE-USE #### - https://docs.litellm.ai/docs/observability/custom_callback#using-your-custom-callback-function

    def log_input_event(self, model, messages, kwargs, print_verbose, callback_func):
        try:
            kwargs["model"] = model
            kwargs["messages"] = messages
            kwargs["log_event_type"] = "pre_api_call"
            callback_func(
                kwargs,
            )
            print_verbose(f"Custom Logger - model call details: {kwargs}")
        except Exception:
            print_verbose(f"Custom Logger Error - {traceback.format_exc()}")

    async def async_log_input_event(
        self, model, messages, kwargs, print_verbose, callback_func
    ):
        try:
            kwargs["model"] = model
            kwargs["messages"] = messages
            kwargs["log_event_type"] = "pre_api_call"
            await callback_func(
                kwargs,
            )
            print_verbose(f"Custom Logger - model call details: {kwargs}")
        except Exception:
            print_verbose(f"Custom Logger Error - {traceback.format_exc()}")

    def log_event(
        self, kwargs, response_obj, start_time, end_time, print_verbose, callback_func
    ):
        # Method definition
        try:
            kwargs["log_event_type"] = "post_api_call"
            callback_func(
                kwargs,  # kwargs to func
                response_obj,
                start_time,
                end_time,
            )
        except Exception:
            print_verbose(f"Custom Logger Error - {traceback.format_exc()}")
            pass

    async def async_log_event(
        self, kwargs, response_obj, start_time, end_time, print_verbose, callback_func
    ):
        # Method definition
        try:
            kwargs["log_event_type"] = "post_api_call"
            await callback_func(
                kwargs,  # kwargs to func
                response_obj,
                start_time,
                end_time,
            )
        except Exception:
            print_verbose(f"Custom Logger Error - {traceback.format_exc()}")
            pass

    #########################################################
    # MCP TOOL CALL HOOKS
    #########################################################
    async def async_pre_mcp_tool_call_hook(
        self, 
        kwargs, 
        request_obj: MCPPreCallRequestObject, 
        start_time, 
        end_time
    ) -> Optional[MCPPreCallResponseObject]:
        """
        This hook gets called before the MCP tool call is made.

        Useful for:
        - Validating tool calls before execution
        - Modifying arguments before they are sent to the MCP server
        - Implementing access control and rate limiting
        - Adding custom metadata or tracking information

        Args:
            kwargs: The logging kwargs containing model call details
            request_obj: MCPPreCallRequestObject containing tool name, arguments, and metadata
            start_time: Start time of the request
            end_time: End time of the request

        Returns:
            MCPPreCallResponseObject with validation results and any modifications
        """
        return None

    async def async_during_mcp_tool_call_hook(
        self, 
        kwargs, 
        request_obj: MCPDuringCallRequestObject, 
        start_time, 
        end_time
    ) -> Optional[MCPDuringCallResponseObject]:
        """
        This hook gets called during the MCP tool call execution.

        Useful for:
        - Concurrent monitoring and validation during tool execution
        - Implementing timeouts and cancellation logic
        - Real-time cost tracking and billing
        - Performance monitoring and metrics collection

        Args:
            kwargs: The logging kwargs containing model call details
            request_obj: MCPDuringCallRequestObject containing tool execution context
            start_time: Start time of the request
            end_time: End time of the request

        Returns:
            MCPDuringCallResponseObject with execution control decisions
        """
        return None

    async def async_post_mcp_tool_call_hook(
        self, kwargs, response_obj: MCPPostCallResponseObject, start_time, end_time
    ) -> Optional[MCPPostCallResponseObject]:
        """
        This log gets called after the MCP tool call is made.

        Useful if you want to modiy the standard logging payload after the MCP tool call is made.
        """
        return None

    # Useful helpers for custom logger classes

    def truncate_standard_logging_payload_content(
        self,
        standard_logging_object: StandardLoggingPayload,
    ):
        """
        Truncate error strings and message content in logging payload

        Some loggers like DataDog/ GCS Bucket have a limit on the size of the payload. (1MB)

        This function truncates the error string and the message content if they exceed a certain length.
        """
        MAX_STR_LENGTH = 10_000

        # Truncate fields that might exceed max length
        fields_to_truncate = ["error_str", "messages", "response"]
        for field in fields_to_truncate:
            self._truncate_field(
                standard_logging_object=standard_logging_object,
                field_name=field,
                max_length=MAX_STR_LENGTH,
            )

    def _truncate_field(
        self,
        standard_logging_object: StandardLoggingPayload,
        field_name: str,
        max_length: int,
    ) -> None:
        """
        Helper function to truncate a field in the logging payload

        This converts the field to a string and then truncates it if it exceeds the max length.

        Why convert to string ?
        1. User was sending a poorly formatted list for `messages` field, we could not predict where they would send content
            - Converting to string and then truncating the logged content catches this
        2. We want to avoid modifying the original `messages`, `response`, and `error_str` in the logging payload since these are in kwargs and could be returned to the user
        """
        field_value = standard_logging_object.get(field_name)  # type: ignore
        if field_value:
            str_value = str(field_value)
            if len(str_value) > max_length:
                standard_logging_object[field_name] = self._truncate_text(  # type: ignore
                    text=str_value, max_length=max_length
                )

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text if it exceeds max_length"""
        return (
            text[:max_length]
            + "...truncated by litellm, this logger does not support large content"
            if len(text) > max_length
            else text
        )

    def _select_metadata_field(
        self, request_kwargs: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Select the metadata field to use for logging

        1. If `litellm_metadata` is in the request kwargs, use it
        2. Otherwise, use `metadata`
        """
        from litellm.constants import LITELLM_METADATA_FIELD, OLD_LITELLM_METADATA_FIELD

        if request_kwargs is None:
            return None
        if LITELLM_METADATA_FIELD in request_kwargs:
            return LITELLM_METADATA_FIELD
        return OLD_LITELLM_METADATA_FIELD
    
    def redact_standard_logging_payload_from_model_call_details(
        self, model_call_details: Dict
    ) -> Dict:
        """
        Only redacts messages and responses when self.turn_off_message_logging is True
        

        By default, self.turn_off_message_logging is False and this does nothing.
        
        Return a redacted deepcopy of the provided logging payload.
        
        This is useful for logging payloads that contain sensitive information.
        """
        from copy import copy

        from litellm import Choices, Message, ModelResponse
        from litellm.types.utils import LiteLLMCommonStrings
        turn_off_message_logging: bool = getattr(self, "turn_off_message_logging", False)
        
        if turn_off_message_logging is False:
            return model_call_details
        
        # Only make a shallow copy of the top-level dict to avoid deepcopy issues
        # with complex objects like AuthenticationError that may be present
        model_call_details_copy = copy(model_call_details)
        redacted_str = LiteLLMCommonStrings.redacted_by_litellm.value
        standard_logging_object = model_call_details.get("standard_logging_object")
        if standard_logging_object is None:
            return model_call_details_copy

        # Make a copy of just the standard_logging_object to avoid modifying the original
        standard_logging_object_copy = copy(standard_logging_object)

        if standard_logging_object_copy.get("messages") is not None:
            standard_logging_object_copy["messages"] = [Message(content=redacted_str).model_dump()]

        if standard_logging_object_copy.get("response") is not None:
            model_response = ModelResponse(
                choices=[Choices(message=Message(content=redacted_str))]
            )
            model_response_dict = model_response.model_dump()
            standard_logging_object_copy["response"] = model_response_dict

        model_call_details_copy["standard_logging_object"] = standard_logging_object_copy
        return model_call_details_copy
