### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw body, then unconditionally trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers — none of which are covered by that HMAC — and hands them to the app's handler as if they were verified/authenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: `to_signable_string` → `@raw_body` [1](#0-0) . `Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string and compares it to the `hmac-sha256`/`x-shopify-hmac-sha256` header [2](#0-1) . Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from separate, unauthenticated headers with no cryptographic tie to the signed body [3](#0-2) .

`Webhooks::Registry.process` uses these unauthenticated fields as the sole source of truth: it looks up the handler by the unauthenticated `request.topic`, and constructs `WebhookMetadata` — passed straight to the app's handler — using the unauthenticated `request.shop`, `request.webhook_id`, and `request.api_version`, with only the request's HMAC-over-body check gating execution: [4](#0-3) 

The library's own documentation confirms apps are expected to treat `shop` from `WebhookMetadata` as the authenticated tenant identity for that event (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [5](#0-4) . Because `shop` and `topic` are not part of the signed content, `HmacValidator.validate` returning `true` proves only "this body was HMAC'd with our secret at some point" — it does not prove which shop or which topic that body was ever associated with. This is the exact bug class from the referenced report: a field that is *acted on* (used to attribute the webhook to a tenant and dispatch a handler) is not covered by the identity-binding check (the HMAC), so the equality `shop authenticated by HMAC == shop delivered to handler` does not actually hold — the second is taken from an independent, unauthenticated header.

### Impact Explanation
Any party capable of obtaining one valid `(raw_body, hmac)` pair for the shared app secret (e.g., an app developer/operator debugging their own webhook deliveries, or a compromised/rogue tenant able to observe deliveries for their own shop) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header (any myshopify.com-style value) and/or `topic` header. `HmacValidator.validate` will still pass because it never inspects those headers, and `Registry.process` will invoke the handler believing the event legitimately originated from the attacker-chosen shop and topic. For webhook handlers that use `data.shop` as the tenant identifier to key session/storage lookups or to drive privileged actions (e.g., `app/uninstalled`, `customers/redact`, `shop/redact`, order or fulfillment processing), this enables cross-tenant data confusion/attribution and can trigger tenant-scoped side effects for a shop the caller does not control — matching the "cross-tenant access" / identity-binding-break impact class.

### Likelihood Explanation
Exploitation does not require the app's `client_secret` or `access_token` — only a single previously observed `(raw_body, hmac)` pair, which can legitimately be produced any time the underlying app processes real webhook traffic (e.g., from the attacker's own installed shop). The header manipulation itself (setting `X-Shopify-Shop-Domain`/`X-Shopify-Topic` to arbitrary values on a POST to the app's public webhook endpoint) requires no privileged access and no cryptographic secret. The main constraint is that the attacker's chosen `topic` must correspond to a body Shopify would plausibly send for that topic, since handlers may assume body shape; this is a modest but not blocking constraint.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` (or at minimum `shop` and `topic`) in the HMAC-signed content that `Webhooks::Request#to_signable_string` covers, or independently verify these header values against Shopify (e.g., confirm the shop is currently installed and the topic/webhook_id pairing is one that was actually registered) before dispatching to the handler. At minimum, document prominently that `shop`/`topic` in `WebhookMetadata` are unauthenticated relative to the HMAC and must not be trusted as tenant identity without additional verification.

### Proof of Concept
1. Attacker installs the target app on a shop they control (or otherwise observes one legitimate webhook delivery), capturing a raw body `B` and its valid header `X-Shopify-Hmac-Sha256: H` (computed over `B` with the app's shared secret) via `OpenSSL::HMAC.hexdigest(...)` as done in `HmacValidator` [6](#0-5) .
2. Attacker POSTs to the app's public webhook endpoint with body `B`, `X-Shopify-Hmac-Sha256: H` (unchanged), but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and/or `X-Shopify-Topic: app/uninstalled` (or another registered topic).
3. `Webhooks::Request.new` parses these headers without validating any binding to `H` [3](#0-2) .
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` [7](#0-6) .
5. The registered handler for the spoofed topic is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: ..., body: parsed(B), ...)` [8](#0-7) , causing the app to act as though this event genuinely originated from `victim-shop.myshopify.com`.

Note: I was unable to fully verify, within this gem alone, whether real-world app deployments expose a way for an unprivileged party to observe a legitimate `(body, hmac)` pair without already controlling the receiving endpoint or being the app operator; this affects the practical ease of step 1 but does not change the underlying code-level flaw that `shop`/`topic`/`webhook_id`/`api_version` are not bound to the HMAC.

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

**File:** docs/usage/webhooks.md (L24-29)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
