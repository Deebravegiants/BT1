### Title
Cross-Tenant Webhook Shop Spoofing — HMAC Signature Does Not Cover the `shop-domain` Header — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then trusts the unauthenticated `x-shopify-shop-domain` (or `shopify-shop-domain`) header as the tenant identity forwarded to the app's handler. Because the header is never part of the signed material, any actor who can obtain one genuine, validly-signed webhook body for their own shop can replay it with a forged `shop-domain` header claiming to be a different tenant, and the library will pass that spoofed identity straight through to the host application as authenticated.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes/compares the signature strictly against `verifiable_query.to_signable_string`. [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw JSON body — none of the Shopify HTTP headers are included in the signable material: [2](#0-1) 

Yet `shop`, `topic`, `webhook_id`, and `api_version` are all derived purely from headers and are never cross-checked against anything bound by the HMAC: [3](#0-2) 

`Registry.process` validates only the HMAC, then immediately constructs `WebhookMetadata` using the unauthenticated `request.shop` value and hands it to the app-registered handler as trusted metadata: [4](#0-3) 

Because a single app's `api_secret_key` is shared across every shop that installs the app, any merchant who legitimately installs the app receives real Shopify webhooks for their own store with a correctly computed HMAC over the body. That merchant can capture such a request and resend it to the app's webhook endpoint, substituting the `x-shopify-shop-domain` header (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) for a victim shop's domain. `HmacValidator.validate` will still succeed because it only re-derives the signature from the (unmodified) body, and `Registry.process` will dispatch the handler believing the event originated from the victim shop — breaking the binding: `shop authenticated by HMAC` ≠ `shop the handler is told owns this event`.

This satisfies the listed analog category "a field acted on but not covered by the HMAC."

### Impact Explanation
Any host application logic in the webhook handler that keys off `WebhookMetadata#shop` (e.g., looking up/activating that shop's stored session or access token, writing data attributed to that shop, triggering side effects scoped to that tenant) can be tricked into operating on the wrong tenant's context using body content the attacker fully controls (since it is their own replayed/self-authored webhook body). This is a cross-tenant confusion primitive rooted entirely in this gem's own `Webhooks::Request`/`Registry` implementation — it does not require the host app to deviate from the documented usage; the documented flow itself (`Registry.process` → handler receives `data.shop`) implicitly treats the header as authenticated when it is not.

### Likelihood Explanation
Requires only that the attacker be a legitimate (even free/trial) merchant who has installed the target app — no `api_secret_key`, access token, or privileged account is needed, matching the "unprivileged internet user" threshold. Capturing one's own real webhook and replaying it with a modified header is straightforward with any HTTP proxy.

### Recommendation
Bind the tenant identity to the HMAC-verified material: incorporate the `shop`/`topic`/`webhook-id` headers (or independently verify `request.shop` against the shop associated with the session/store the handler expects) before trusting `WebhookMetadata#shop` in `Registry.process`. At minimum, `docs/usage/webhooks.md` and `WebhookMetadata` should explicitly document that `shop` is unauthenticated header data and must be independently validated by the host application against its own shop/session records before use.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker.myshopify.com`.
2. Trigger any webhook event registered by the app; capture the genuine request Shopify sends, including its valid `x-shopify-hmac-sha256` header (computed over the JSON body with the app's `api_secret_key`).
3. Replay the exact same raw body/HMAC to the app's webhook endpoint, but change the `x-shopify-shop-domain` header to `victim.myshopify.com` (and optionally topic/webhook-id).
4. `HmacValidator.validate` succeeds (body unchanged) at `lib/shopify_api/utils/hmac_validator.rb:13-22`, `Registry.process` at `lib/shopify_api/webhooks/registry.rb:188-200` builds `WebhookMetadata` with `shop: "victim.myshopify.com"` and invokes the handler — which now believes the event is authentically from the victim tenant.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
