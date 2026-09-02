Confirmed: `Utils::VerifiableQuery#to_signable_string` is the only material bound by the HMAC, and for webhooks `Request#to_signable_string` returns solely `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers with no cryptographic binding to that signature [2](#0-1) . `Registry.process` only calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (raw body) and compares it to the `hmac` header [3](#0-2) [4](#0-3) . Since the `api_secret_key` is shared across every shop that installs the app, this is a genuine identity-binding gap matching the report's bug class.

### Title
Webhook shop-domain header is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` attributes consumed by `Registry.process` and handed to the app's webhook handler come straight from unauthenticated HTTP headers. Because the app's `api_secret_key` is identical for every shop that installs the app, any tenant that can obtain one genuine (body, HMAC) pair — for example by installing the app on their own store and receiving a real webhook — can replay that exact body to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header, and the library will accept it as authentic and attribute it to an arbitrary shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are pulled from headers and are never mixed into the HMAC computation: [2](#0-1) 

`HmacValidator.validate` verifies only the body against the shared `Context.api_secret_key` (or `old_api_secret_key`): [5](#0-4) 

`Registry.process` trusts this validation, then constructs `WebhookMetadata` using `request.shop` taken straight from the unauthenticated header and dispatches it to the host application's handler: [3](#0-2) 

The equality that should hold is: `shop authenticated by HMAC == shop delivered to the handler`. In this implementation, the HMAC authenticates only the body bytes, so `shop header != value covered by signature`. Any party possessing one valid `(body, hmac)` pair signed with the app's `api_secret_key` — trivially obtainable by installing the app on their own store — can resubmit that pair to the webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header value and have it accepted as a legitimate webhook for that other shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: a webhook nominally "verified" as authentic can be attributed to any shop the attacker chooses, not only the shop that actually produced it. Any host application logic that trusts `WebhookMetadata#shop` (e.g., looking up per-shop configuration/secrets, triggering shop-scoped side effects, or treating `shop/redact`, `customers/redact`, `customers/data_request` mandatory topics as coming from a specific tenant) can be fed cross-tenant data, which falls under cross-tenant access.

### Likelihood Explanation
Exploitability requires only the ability to send arbitrary HTTP requests to the app's public webhook endpoint (no leaked secret needed) plus one genuine webhook body, which any merchant installing the app on their own development store can obtain trivially and then replay against the same public endpoint with a modified shop header, and payloads that are content-independent of the shop (e.g., minimal/mandatory-topic payloads or webhooks whose body doesn't embed shop-identifying data) make this straightforward.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the value that is HMAC-verified (or otherwise cryptographically bind them to the body/signature), or independently validate that the `shop` header corresponds to a shop actually known/installed by the app before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook (e.g., `app/uninstalled`) with `raw_body = B` and header `X-Shopify-Hmac-Sha256 = HMAC(secret, B)`.
2. Attacker sends a new HTTP POST to the app's public webhook endpoint with the same body `B` and the same `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (i.e., `B`) and matches it against the supplied header — validation succeeds because the shop header was never part of the signed content [6](#0-5) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, even though the webhook actually originated from the attacker's own store.

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
