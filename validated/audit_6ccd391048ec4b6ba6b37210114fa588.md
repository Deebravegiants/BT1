This confirms the finding. The webhook `hmac` signature (`Utils::HmacValidator.validate`) only covers `to_signable_string`, which for `Webhooks::Request` is the raw body (`lib/shopify_api/webhooks/request.rb:35-38`). The `shop` value (and `topic`, `api_version`, `webhook_id`) come from unauthenticated HTTP headers (`shopify-shop-domain` / `x-shopify-shop-domain`) that are never included in the signable string, so they are never covered by the HMAC.

### Title
Webhook `shop` identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by checking `Utils::HmacValidator.validate(request)`, which recomputes an HMAC over `request.to_signable_string` (the raw body only) and compares it to the `X-Shopify-Hmac-SHA256` header. The `shop` attribute used downstream to attribute the event to a tenant is read from the `X-Shopify-Shop-Domain` header, which is not part of the signed material at all.

### Finding Description
The identity binding that should hold is:
`shop authenticated by HMAC == shop used by the handler`

In `Webhooks::Request` (`lib/shopify_api/webhooks/request.rb:20-23,35-38`), `shop` is read from a raw header: [1](#0-0) 

while `to_signable_string`, the only input to the HMAC comparison, returns just `@raw_body`: [2](#0-1) 

`Registry.process` validates the HMAC and, if it matches, immediately trusts `request.shop` to construct `WebhookMetadata` for the handler: [3](#0-2) 

Because every shop that has an app installed shares the same app-level `client_secret` (`Context.api_secret_key`) for computing the webhook HMAC (confirmed in `Utils::HmacValidator.validate_signature`, which signs with `Context.api_secret_key`/`old_api_secret_key` rather than a per-shop secret): [4](#0-3) 

a valid HMAC for a genuine webhook delivered to the app for **shop A** is also a byte-for-byte valid HMAC for the identical raw body relabeled as originating from **shop B**, because the shop header plays no role in the signature computation.

### Impact Explanation
An unprivileged user who can install the target app on their own store (any developer/merchant can do this for a public app) receives genuine, correctly-signed webhook deliveries for their own shop. By capturing one such raw request (raw body + valid `hmac-sha256` header) and replaying it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain, the attacker can make the host application's handler process (`WebhookHandler#handle`) attacker-controlled data while believing it originates from an arbitrary other tenant. Since `HmacValidator.validate` still returns `true` (the raw body/signature pair is untouched), `Registry.process` never rejects the forged request. This is a cross-tenant identity confusion: the app cannot distinguish "webhook genuinely about shop B" from "attacker's own webhook body relabeled as shop B." Depending on how the host app uses `WebhookMetadata#shop` (e.g. as a DB lookup key for tenant data, to trigger data deletion/redaction flows such as `customers/redact`/`shop/redact`, or to update tenant-specific state), this can lead to cross-tenant data corruption or privileged actions being attributed to the wrong tenant.

### Likelihood Explanation
Likelihood is high for any application that installs the app on more than one shop and relies on the gem's `Webhooks::Registry.process`/`Webhooks::Request` for authentication, since the exploit requires no secret material — only the ability to install the app once (as any unprivileged developer/merchant can) and to replay an HTTP request with a modified header.

### Recommendation
Bind the tenant identity to the signed payload before trusting it: include the shop domain (and ideally topic/webhook id) inside the value that is HMAC-verified, or, at minimum, require the caller to independently corroborate `request.shop` against a known/expected shop (e.g., the session used to register the webhook) rather than trusting the unauthenticated header. Shopify's own webhook payloads typically embed shop-identifying data in the body for many topics; `to_signable_string` should not silently ignore the headers that this library exposes as authenticated (`shop`, `topic`, `webhook_id`).

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify sends a genuine webhook with a valid `X-Shopify-Hmac-SHA256` header computed over the raw JSON body using the app's `client_secret`.
2. Capture the raw request: `raw_body` and header `X-Shopify-Hmac-Sha256: <valid_hmac>`.
3. Replay this exact `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and `X-Shopify-Topic`/`X-Shopify-Webhook-Id` as desired.
4. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)`, which only checks `HMAC(raw_body, api_secret_key) == received_hmac` — this still passes because `raw_body` and `hmac` are untouched. [5](#0-4) 
5. The handler executes with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: attacker_controlled_body, ...)`, believing the attacker-crafted payload legitimately originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
