### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before dispatching it to a handler, but the HMAC it checks only covers the raw request body. The `shop-domain`, `topic`, and `webhook-id` values — which are taken straight from unauthenticated HTTP headers — are never included in the signed content, yet they are exactly the fields the handler uses to attribute the payload to a merchant/tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC purely from `to_signable_string`, i.e. the body, and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` uses this single check as the sole authenticity gate before handing the caller-supplied `request.shop`/`request.topic`/`request.webhook_id` straight to the handler as trusted metadata: [4](#0-3) 

The identity binding that should hold is: `shop asserted to the handler == shop whose secret actually produced this signed payload`. Because the HMAC only covers the body, that equality is never enforced — the `shop-domain` header can be swapped to any value while the same (body, hmac) pair remains valid. An attacker who has legitimately installed the app on their own shop receives real webhooks with a valid `hmac-sha256` header computed from the shared app `client_secret`. They can capture one such `(raw_body, hmac)` pair and POST it to the app's public webhook endpoint again, this time with the `shop-domain` header changed to any victim shop domain (and, if useful, a different `topic`/`webhook-id`). `HmacValidator.validate` still returns `true` because it never inspected those headers, and `Registry.process` dispatches the payload to the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain.

### Impact Explanation
Host applications are documented to key their per-merchant record lookups off exactly this `shop` value (see the `shopify_app` gem's reference `ShopSessionStorage#retrieve(id)` pattern referenced in this repo's own docs, which looks up merchant records by `shopify_domain`). A forged webhook that is "valid" per this gem's HMAC check but carries an arbitrary `shop` claim lets an unprivileged attacker inject fabricated events attributed to any other merchant using the app — a cross-tenant data-integrity/confusion issue with no attacker-side credential requirement beyond a normal app install. This satisfies the High-impact "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation only requires: (1) installing the target app on an attacker-controlled shop (ordinary, unprivileged action available to any merchant/developer), (2) capturing one genuine webhook body+HMAC pair sent to the attacker's own endpoint, and (3) replaying it to the same public webhook endpoint with a modified `shop-domain`/`topic`/`webhook-id` header. No access to `api_secret_key`, access tokens, or the victim's credentials is needed, making this readily reachable by any internet user who can self-install the app.

### Recommendation
Bind the trust-relevant headers into the signed content that `HmacValidator` verifies (e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or require the host application to independently authenticate the shop before trusting `WebhookMetadata.shop`), and document clearly that `Registry.process`'s HMAC check does not itself authenticate the `shop-domain`/`topic`/`webhook-id` headers.

### Proof of Concept
1. Install the target Shopify app on an attacker-owned development shop; register a webhook for a topic such as `orders/create`.
2. Capture a delivered webhook's exact `raw_body` and its `X-Shopify-Hmac-Sha256` header value (both are valid and will pass `HmacValidator.validate`).
3. Replay the identical `raw_body` and `hmac` to the app's public webhook endpoint, but set `X-Shopify-Shop-Domain` to the victim shop's domain (and optionally change `X-Shopify-Topic`/`X-Shopify-Webhook-Id`):
```ruby
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(
    raw_body: captured_raw_body,
    headers: {
      "x-shopify-topic" => "orders/create",
      "x-shopify-hmac-sha256" => captured_hmac,
      "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
      "x-shopify-webhook-id" => "attacker-controlled-id",
    },
  ),
)
```
4. `Utils::HmacValidator.validate` returns `true` (it only checked the body), and the registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, even though the payload never originated from that shop.

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
