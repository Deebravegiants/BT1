### Title
Webhook `shop-domain` (and topic/webhook-id) header is not covered by the HMAC signature, allowing cross-tenant shop spoofing on webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the HMAC over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — all read from HTTP headers — are never included in the signed payload. `Registry.process` trusts `request.shop` as the tenant identity when dispatching to the app's webhook handler, without that value being bound by the HMAC. This breaks the identity binding: `hmac == HMAC(secret, body)` while `shop` (the tenant identifier acted upon) is `!= covered_by(hmac)`.

### Finding Description
`Registry.process` validates the webhook solely via `Utils::HmacValidator.validate(request)` and then immediately builds `WebhookMetadata` from `request.shop`, `request.topic`, etc., passing it to the app's handler: [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes the signature from `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw HTTP body — none of the identity headers are included: [3](#0-2) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are parsed straight from unauthenticated headers: [4](#0-3) 

Because the signature only certifies the byte content of the body, any request whose body byte-for-byte matches a body the app secret was once used to sign for topic/shop A will still pass HMAC validation even if the `shop-domain`/`topic`/`webhook-id` headers are swapped to claim shop B. This is the exact pattern flagged in the source report: a field the code acts on (`shop`, used as the tenant key when dispatching to the handler) is not covered by the same authentication check (HMAC) that is used to accept the request.

Concretely: bodies for many webhook topics are either fixed/predictable (e.g., `app/uninstalled` webhooks with minimal or templated JSON, or webhooks whose payload the attacker's own shop can legitimately receive) or, more generally, any legitimate webhook a merchant's own shop receives from Shopify carries a valid HMAC over that exact body. A merchant who has installed the app (an "unprivileged" actor relative to other tenants) can capture the body+HMAC of a webhook legitimately delivered to their own store and replay it to the app's webhook endpoint with the `shop-domain` (and/or `topic`) header rewritten to point at a different shop. `HmacValidator.validate` will still return `true` because it never looks at those headers, and `Registry.process` will hand the forged `shop` value to the handler as if the event genuinely originated from that other tenant.

### Impact Explanation
This crosses a tenant boundary: the webhook handler receives attacker-controlled `shop` identity backed by a signature that does not actually certify that identity. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to look up/create sessions, update per-shop billing/subscription state, or trigger per-tenant side effects such as data deletion on `shop/redact`), this enables cross-tenant confusion/spoofing of webhook origin — matching the "Critical: cross-tenant access" impact category, since the gem itself asserts webhook authenticity is proven once `HmacValidator.validate` passes, but that check does not actually bind the shop identity.

### Likelihood Explanation
Likelihood is moderate: the attacker needs a body+HMAC pair that Shopify actually signed (there is no way to forge the HMAC without `api_secret_key`), so this is not a blind forgery. However, any merchant that installs the app receives legitimately-signed webhooks for their own store and can trivially capture and replay them with modified identity headers, since none of the framework, transport, or gem-level checks bind `shop-domain`/`topic`/`webhook-id` to the signed bytes. No leaked credentials or privileged access are required — only the ability to receive one's own app webhooks and replay HTTP requests.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed/verified material for webhooks, or otherwise cryptographically bind them to the raw body before trusting `request.shop` in `Registry.process`. At minimum, `Utils::HmacValidator` should validate that the header-derived shop matches an expected/registered value (e.g., cross-checked against the session/shop the webhook was registered for) rather than accepting any header value once the body-only HMAC passes.

### Proof of Concept
1. App has webhook endpoint using `ShopifyAPI::Webhooks::Registry.process(request)`.
2. Attacker's own store (`attacker-shop.myshopify.com`) has the app installed and legitimately receives a real webhook from Shopify: body `B`, headers include `x-shopify-hmac-sha256: H` (valid HMAC of `B`), `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: some/topic`.
3. Attacker replays the exact same body `B` and HMAC `H` to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally the topic/webhook-id headers).
4. `Utils::HmacValidator.validate` only checks `HMAC(secret, B) == H`, which still holds, so validation succeeds: [5](#0-4) 
5. `Registry.process` proceeds to call the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, where `shop` is now `victim-shop.myshopify.com` even though the signed body never certified that shop: [6](#0-5)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
```
