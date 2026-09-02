## Finding

The webhook HMAC validation in this gem only authenticates the raw request body — it never binds the `shop`, `topic`, `webhook_id`, or `api_version` identifiers that the registry actually acts on. This is a direct analog to the "mixed identity, unauthenticated field" class in the report: an attacker-controlled field (`shop`) is acted upon by privileged logic while a *different* field (`raw_body`) is the only thing covered by the signature.

### Title
Webhook shop/topic identity headers are not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  which is what `Utils::HmacValidator.validate` verifies against the HMAC secret [2](#0-1) . However, `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers that are completely outside the signed payload [3](#0-2) , and `Registry.process` uses these unauthenticated header values both to select the handler (`request.topic`) and to construct the `WebhookMetadata` (`request.shop`, etc.) delivered to the app's handler [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop that produced the signed body == shop the handler is told owns this webhook`. Because `to_signable_string` only ever returns `@raw_body`, changing the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, `x-shopify-topic`, or `x-shopify-webhook-id` header does not invalidate `Utils::HmacValidator.validate(request)` — the HMAC only proves the body bytes were produced with the app's secret, not that the accompanying headers are genuine.

Any actor who can obtain one genuinely-signed webhook delivery for a shop they control (installing the app on their own store, an unprivileged action any internet user can perform) can capture that request and replay it with the `shop-domain` (and/or `topic`/`webhook-id`) header swapped to another shop's domain or a different topic, while keeping the original signed body. `HmacValidator.validate` still passes because it re-derives the signature purely from `@raw_body` [5](#0-4) [6](#0-5) . `Registry.process` then dispatches to the handler for the (attacker-chosen) `request.topic`, and hands the handler a `WebhookMetadata` whose `shop` field is the attacker-chosen domain [4](#0-3) .

### Impact Explanation
Host applications built on this gem are documented to rely on `WebhookMetadata#shop`/`topic` as the trusted tenant identity for the delivered event (see `Registry.process` passing `request.shop` straight into the handler). An attacker who forges the `shop-domain` header while reusing a validly-signed body can make the app process/act on data under a shop it does not control — e.g. triggering `shop/redact` or `customers/redact` handling for an arbitrary target shop, or writing attacker-supplied body content into another tenant's records — a cross-tenant integrity/confidentiality violation, which maps to the Critical "cross-tenant access" category.

### Likelihood Explanation
The only prerequisite is the ability to receive one legitimately HMAC-signed webhook, which any unprivileged developer can obtain by installing the app on their own development store. From there, replaying with modified headers requires no secret material at all, since the signature never covers the headers. This is a low-effort, no-privilege attack path.

### Recommendation
Include the shop domain, topic, and webhook id in the signed/verified payload (or otherwise cryptographically bind them, e.g. by having `to_signable_string` incorporate a canonicalized header string alongside the raw body), and verify that the resulting values match what's used to route/act on the webhook in `Registry.process` before dispatch.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, triggering Shopify to send a webhook such as `orders/create`, correctly signed with the app's `api_secret_key` over the JSON body.
2. Attacker captures this raw POST (headers + body).
3. Attacker resends the same body/signature to the app's webhook endpoint but rewrites `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and, if desired, `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only checks `@raw_body` against the HMAC [1](#0-0) .
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-forged `shop` value [7](#0-6) , causing the host app to process the payload as if it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
