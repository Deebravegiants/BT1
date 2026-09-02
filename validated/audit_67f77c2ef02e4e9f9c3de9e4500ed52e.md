### Title
Webhook `shop`, `topic`, and `webhook_id` identity fields are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` extracts the tenant-identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) directly from unauthenticated HTTP headers, but `Utils::HmacValidator` only verifies the HMAC over the raw request body. Any two values that can be authenticated together (a `raw_body` + its Shopify-issued HMAC) can be replayed with an arbitrary `shop-domain`/`topic` header and will still pass validation, because those header values are never part of the signed content.

### Finding Description
The signable content for a webhook request is defined as: [1](#0-0) 

`to_signable_string` returns only `@raw_body`. Verification is done purely against that string: [2](#0-1) 

Meanwhile, `shop`, `topic`, and `webhook_id` are pulled straight from headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` trusts these header-derived fields to dispatch to the merchant-specific handler: [4](#0-3) 

The broken identity binding, stated as an equality that the library implicitly assumes but never enforces:
`HMAC_valid(raw_body) == true` is treated as proof that `(shop, topic, webhook_id)` in the headers are authentic, when in fact only `raw_body` is authenticated. Before the attack, a legitimate `(raw_body, hmac)` pair is associated with the *originating* shop that produced it (via Shopify's real webhook delivery). After the attack, the same `(raw_body, hmac)` pair is replayed with attacker-chosen `shop-domain`/`topic` headers, and `HmacValidator.validate` still returns `true` since it never inspects those headers.

### Impact Explanation
This breaks the cross-tenant boundary the gem is supposed to preserve for webhook events. An unprivileged internet user who can install the target app on their own (attacker-controlled) development shop will receive genuine, correctly-signed webhook deliveries from Shopify for that shop (the app's `client_secret` is shared across all installs, so the HMAC key is the same for every tenant). The attacker can capture one such `(raw_body, hmac)` pair — many webhook bodies are minimal or attacker-influenced (e.g. `app/uninstalled`, `shop/update`, or a webhook fired by an action the attacker performs in their own store) — and replay it directly to the app's webhook endpoint with `x-shopify-shop-domain` set to a victim shop and `x-shopify-topic` set to any topic the host app has registered a handler for. `Registry.process` will validate successfully and invoke the app's handler believing the event legitimately originated from the victim shop. Depending on the handler's logic, this enables cross-tenant impersonation of shop lifecycle/business events (e.g., forcing an app to treat a victim shop as uninstalled, or applying attacker-supplied resource data under the victim's identity), which matches the "cross-tenant access" high-impact category.

### Likelihood Explanation
Requires only an app install on an attacker-owned shop (unprivileged, no credentials, no access token, no `api_secret_key` needed) plus the ability to send an arbitrary HTTP POST to the app's public webhook endpoint. No TLS interception, social engineering, or privileged access is needed. The main precondition is that the host application's webhook handler makes a security-relevant decision keyed on `WebhookMetadata#shop`/`#topic`, which is the intended and documented usage pattern shown in the gem's own webhook docs.

### Recommendation
Bind the identity headers into the HMAC-covered content, e.g. by including `shop`, `topic`, and `webhook_id` in `to_signable_string` (or by requiring/verifying them against out-of-band knowledge such as a registered shop/session lookup) before dispatching to a handler, so that a signature valid for one shop/topic cannot be replayed for another.

### Proof of Concept
1. Install the target app (built on this gem) on an attacker-controlled dev store; trigger any webhook topic the app has registered (e.g. `app/uninstalled`), and capture the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` that Shopify sent (valid because it's HMAC-SHA256(`B`, shared `client_secret`)).
2. Replay the request to the same endpoint with modified headers:
```
POST /webhooks HTTP/1.1
X-Shopify-Topic: app/uninstalled
X-Shopify-Hmac-Sha256: H
X-Shopify-Shop-Domain: victim-shop.myshopify.com
X-Shopify-Webhook-Id: attacker-chosen

<B>
```
3. `HmacValidator.validate` succeeds because `H` is a valid HMAC of `B`, regardless of the `Shop-Domain`/`Topic` headers.
4. `Registry.process` dispatches to the `app/uninstalled` handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`, causing the host app to act as if the victim shop uninstalled the app.

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
