### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` header — which is never part of the signed material — to identify which merchant/tenant the payload belongs to. This breaks the intended binding `HMAC(secret, signed_bytes) == received_hmac` ⇒ `shop header is authentic`, because `signed_bytes` (the raw body) and `shop` (a header) are disjoint fields.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read from HTTP headers independent of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e. `raw_body` only) and compares it to the `hmac` header via `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` uses this HMAC check as the sole authenticity gate, then immediately trusts `request.shop` (the unauthenticated header) to build `WebhookMetadata` and dispatch it to the app's handler: [4](#0-3) 

`WebhookMetadata.shop` is a plain, unvalidated `String` field passed straight to the app's `WebhookHandler#handle`: [5](#0-4) 

Because the HMAC is computed only over the raw JSON body and the app's single shared `api_secret_key` is identical for every shop connected to the app, any valid `(raw_body, hmac)` pair legitimately obtained for **shop A** remains a cryptographically valid pair for **any other shop header value**, since the secret and the signed bytes do not depend on which shop is claimed. An attacker who controls (or is) a merchant with the app installed can capture one legitimate webhook delivery from Shopify to their own shop (a completely normal, unprivileged action — no `api_secret_key` or access token needed), then replay that exact raw body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with a victim shop's domain. The HMAC check still passes (it never inspected the header), and the handler receives `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's own webhook payload>)`.

This is the "field acted on but not covered by the HMAC" identity-binding break described in the bug-class hint: the equality the code implicitly assumes — `hmac_valid(raw_body) ⇒ shop_header_is_authentic` — does not hold, because `shop_header` is disjoint from `raw_body` in the signed message.

### Impact Explanation
This crosses a tenant boundary within the gem's own trust logic: it allows one merchant/attacker to inject data attributed to a different merchant's shop into the host application's webhook processing pipeline, entirely through this gem's public `Registry.process`/`Request` API and without any credentials beyond a normal app installation on their own store. Depending on what the host app's webhook handler does with `data.shop` (e.g., look up/update the target shop's records, sync inventory, cancel orders, mark the shop as uninstalled via `app/uninstalled`, etc.), this enables cross-tenant data corruption or unauthorized actions attributed to a victim shop — meeting the "cross-tenant access" bar for a Critical/High finding.

### Likelihood Explanation
Likelihood is meaningful but bounded: the attacker must install the app on a shop they control (an ordinary, unprivileged action for any Shopify merchant/developer) and capture at least one real webhook delivery (trivial — just log server headers/body). They then replay it with a forged shop header. No secrets are required. The main constraint is that the attacker only controls the body content of *their own* previously-received webhook topics (e.g., `orders/create` from their own test store), so the payload content is attacker-influenced but the `shop` attribution is fully forgeable.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed material, or independently verify that the `shop-domain` header corresponds to a shop with an active session/installation known to the app *before* trusting it, rather than relying on an out-of-band header that the HMAC never covers. At minimum, document loudly that `WebhookMetadata#shop` is unauthenticated and host apps must cross-check it against their own installed-shop registry before acting on it.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook topic the app subscribes to (e.g., `orders/create`) and capture the raw POST: headers (`x-shopify-hmac-sha256`, `x-shopify-topic`, `x-shopify-shop-domain: attacker.myshopify.com`) and raw body.
2. Replay the exact same request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim.myshopify.com`, keeping `x-shopify-hmac-sha256` and the raw body byte-for-byte identical.
3. `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only [3](#0-2)  — it matches, so `Registry.process` proceeds and invokes the handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's crafted body>, ...)` [6](#0-5) .
4. The host app's handler processes attacker-supplied data as if it originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
