Found a concrete analog. The webhook HMAC verification in this gem only covers the raw JSON body — none of the identifying headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) are bound into the signed string, yet those exact header values are what the library uses to route and attribute the webhook. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook shop/topic headers are trusted without HMAC binding, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` verifies the HMAC solely against the JSON body. The `shop`, `topic`, `api_version`, and `webhook_id` values — all read directly from unauthenticated HTTP headers — are never part of the signed material, yet `Registry.process` passes `request.shop` and `request.topic` straight into `WebhookMetadata` handed to the app's business-logic handler.

### Finding Description
`Request#to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [4](#0-3) 

`shop`, `topic`, `api_version`, and `webhook_id` are pulled from headers with no cryptographic tie to the signature:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [5](#0-4) 

`HmacValidator.validate_signature` computes the signature purely from `verifiable_query.to_signable_string` (the body) and compares it against the `hmac` header:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [6](#0-5) 

`Registry.process` only checks that the HMAC validates, then forwards the unverified `shop` and `topic` header values to the handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [7](#0-6) 

**Broken identity binding:** the equality the system needs to hold is `hmac_signed_bytes == bytes_that_determine_which_shop/topic_the_payload_is_attributed_to`. Here, `hmac_signed_bytes = raw_body` while `bytes_that_determine_attribution = shop-domain/topic headers`, which are disjoint. Because a single app's `api_secret_key` is shared across every shop that installs it, any unprivileged merchant who installs the app on their own store receives a webhook whose body+HMAC are validly signed with that shared secret. That merchant can capture the `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header rewritten to name a different, victim shop. `HmacValidator.validate` still returns `true` because it never inspected those headers, and `Registry.process` dispatches the forged event to the handler labeled with the attacker-chosen `shop`.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker with only their own (unprivileged) shop installation can make the app process/attribute webhook data as belonging to an arbitrary other shop domain. Any host application logic that keys off `WebhookMetadata#shop` (e.g., updating merchant records, triggering `app/uninstalled` cleanup, syncing order/customer data, disabling/enabling merchant features) can be corrupted or manipulated for a shop the attacker does not control, which falls under the "cross-tenant access" critical-impact category.

### Likelihood Explanation
Any developer/merchant who can install the target app on a store they control (a normal, unprivileged action) can obtain a body+HMAC pair signed with the app's shared secret and immediately reuse it against the same endpoint with a forged shop header — no access token, `client_secret`, or privileged credentials are required, and no interaction with the victim is needed.

### Recommendation
Bind the identifying headers into the verified signature material (or otherwise cryptographically tie `shop`, `topic`, `webhook_id` to the request), and/or validate that the `shop` header corresponds to a shop with an active, matching webhook subscription/session before dispatching to handlers, so that swapping these headers invalidates the HMAC.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Shopify delivers a legitimate webhook (e.g., `orders/create`) to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`.
3. Attacker captures `raw_body` and the valid `hmac` header value.
4. Attacker (or anyone with network access to the app's public webhook route) POSTs the same `raw_body` with the same `hmac`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` because it only checks `raw_body` against the secret.
6. `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and invokes the app's handler, which now believes this event originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
