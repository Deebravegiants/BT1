### Title
Webhook `shop`, `topic`, `webhook-id`, and `api-version` fields are trusted for dispatch and cross-tenant identification despite not being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, but the shop identity, topic, webhook id, and API version used to route and label the webhook are all taken from HTTP headers that are excluded from that signature. Any actor who can obtain one validly-signed webhook body (e.g., by installing the app on their own shop) can replay that exact body with forged `shop-domain`/`topic` headers to make the gem accept and dispatch the payload under a different shop's identity, without needing `api_secret_key`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all read from headers, which are never part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` only compares the HMAC of `to_signable_string` (the body) against the `hmac` header: [3](#0-2) 

`Webhooks::Registry.process` then uses the *unauthenticated* `request.topic` to select the handler, and forwards the *unauthenticated* `request.shop`, `webhook_id`, and `api_version` straight into `WebhookMetadata` that is handed to the app's handler as trusted data: [4](#0-3) 

This exactly mirrors the reported bug class: a field (`shop`/`topic`) that is *acted on* by the security-relevant logic (handler dispatch, `WebhookMetadata.shop`) is not covered by the identity-binding signature (HMAC), so the equality the code implicitly relies on — "the shop/topic in the signed data == the shop/topic the app trusts" — does not actually hold. The HMAC only proves "this body byte

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
