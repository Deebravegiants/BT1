## Title
Webhook shop identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts these header-derived values, including `shop`, when dispatching to the app's handler. Because the shop identity is not bound to the signature, any holder of one valid (body, HMAC) pair — obtainable simply by installing the app on any store, since the signature is generated with the app-wide `client_secret` rather than a per-shop secret — can replay that pair to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header naming a different, victim shop. The signature check still passes, and the handler processes attacker-controlled data as if it belongs to the victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from request headers with no cryptographic binding: [2](#0-1) 

`HmacValidator.validate_signature` verifies the HMAC exactly against `to_signable_string`, i.e. the body alone: [3](#0-2) 

`Registry.process` accepts the request once the (body-only) HMAC check passes, and then constructs `WebhookMetadata` directly from the request's header-derived `shop`, `topic`, and `webhook_id`, handing them to the app's handler as trusted values: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:
`shop_covered_by_hmac == shop_used_for_tenant_routing` is false — the HMAC only authenticates `raw_body`, but `request.shop` (an unauthenticated header) is what `Registry.process` uses as the tenant identity passed to the handler.

Because Shopify signs webhooks with the app's single `client_secret` (not a per-shop secret), a valid `(raw_body, hmac)` pair generated for a legitimate webhook sent to the attacker's own shop remains a valid pair for that body no matter which `shop-domain` header accompanies it. An attacker who has installed the app on any store (including a free development store) can capture such a pair and resend the raw body with the same HMAC but a different `shop-domain` header pointing at a victim shop that also has the app installed.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: an unprivileged party who merely installs the app can inject data attributed to another merchant's shop into the app's webhook handling logic (e.g. faking `orders/create`, `customers/data_request`, `app/uninstalled`, etc. for a shop they don't control), without ever needing that victim's credentials or the app's `client_secret`. Depending on how the host app's handler uses `data.shop` (e.g. to look up sessions, update per-tenant records, or trigger side effects), this can result in cross-tenant data corruption or unauthorized actions being taken against another merchant's account — a cross-tenant access issue.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the target app on some shop (a normal, unprivileged action many public apps allow anyone to do, including via free development stores) and be able to send arbitrary HTTP requests to the app's public webhook endpoint — both trivially available to any internet user targeting an app that embeds this gem's `Webhooks::Registry.process`/`Request` for webhook handling.

### Recommendation
Bind the tenant/topic identity into the signed payload verification path, or otherwise cryptographically tie the `shop-domain` header to the signature before trusting it for routing. Concretely, `Registry.process` (or `Request`) should independently corroborate the claimed shop against something authenticated — e.g. require the caller to supply the expected shop and compare it, or extend the signable string used for verification to include the header fields relied upon downstream — before constructing `WebhookMetadata` and dispatching to handlers.

### Proof of Concept
1. Install the target Shopify app (which uses `ShopifyAPI::Webhooks::Registry`) on an attacker-controlled shop `attacker.myshopify.com`.
2. Trigger any webhook event; capture the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sends (a valid HMAC over that body, computed with the app's `client_secret`).
3. Replay the exact same body and HMAC header to the app's webhook endpoint, but override the `X-Shopify-Shop-Domain` header to `victim.myshopify.com` (a real shop with the app installed) and set `X-Shopify-Topic` to a topic of choice.
4. `HmacValidator.validate` (via `Utils::HmacValidator.validate_signature`, `lib/shopify_api/utils/hmac_validator.rb:26-31`) passes because it only checks the body.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", ...)` and invokes the app's handler as though the event genuinely originated from `victim.myshopify.com`.

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
