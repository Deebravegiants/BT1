### Title
Webhook `shop-domain` header trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop-domain` header (which is *not* part of the signed material) to identify which tenant the webhook belongs to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers and are never mixed into the signed string: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which only calls `request.to_signable_string` (i.e., the raw body) against the computed HMAC, and — once that check passes — immediately dispatches to the handler using `request.shop` taken from the untrusted header: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(api_secret_key, signable_string)` and compares it to the header-provided HMAC using `secure_compare`: [4](#0-3) 

Because the `api_secret_key` is the same for *every* shop that installs a given app, any two webhooks delivered to that app for *different* shops but with byte-identical bodies (e.g. topics with minimal/empty bodies, or a body an attacker-merchant can reproduce) will carry the exact same valid HMAC. A merchant who legitimately controls Shop A can capture a real, correctly-signed webhook delivered to their own endpoint, then replay it

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
