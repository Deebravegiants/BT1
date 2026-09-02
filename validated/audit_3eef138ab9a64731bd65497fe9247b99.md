This confirms the finding: the `shop` field delivered to the webhook handler as the tenant identifier is taken directly from the unauthenticated HTTP header (`shop-domain`), while the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator.validate` only covers the raw request body via `Request#to_signable_string`.

### Title
Webhook `shop` tenant identifier is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then hands the handler a `shop` value taken from an HTTP header that is never included in that signature. Since the app's webhook secret (`api_secret_key`) is shared across every shop that installs the app, any body+HMAC pair captured from one legitimate shop's webhook can be replayed with a different, attacker-chosen `shop-domain`/`x-shopify-shop-domain` header, causing the handler to process data under the wrong tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` reads the signature purely from the `hmac-sha256` header [1](#0-0) , and `to_signable_string`, which is what `HmacValidator` actually signs/verifies, returns only `@raw_body` [2](#0-1) . The `shop` accessor is read independently from the `shop-domain` header, which is not part of the signable content [3](#0-2) .

`Registry.process` validates the HMAC and, if it passes, immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3)  The handler receives this `shop` as the tenant identifier with no independent verification: [5](#0-4) 

The equality that should hold but does not is: `shop bound by HMAC == shop delivered to handler`. Because `HmacValidator.validate` only proves that the *body bytes* were signed with the app's secret—not that the *shop header* was—an attacker who obtains any single valid `(raw_body, hmac)` pair from the app's webhook secret (e.g., by installing the app on their own store and capturing one of its own outgoing webhooks) can resend that same body/HMAC to the app's webhook endpoint while substituting a different shop's domain in the `shop-domain` header. `HmacValidator.validate` at `lib/shopify_api/utils/hmac_validator.rb:13-22` still passes because it never inspects the header, and the handler will execute business logic (e.g., app-installed/data-request/redact logic, order/customer sync, or authorization decisions keyed by shop) believing the event originated from the victim shop.

This directly matches the reported bug class: a field that is acted upon (the tenant/shop identity used by the handler) is not covered by the authentication mechanism (HMAC) meant to bind it, letting an attacker "confuse" the two into crossing tenant boundaries.

### Impact Explanation
This allows cross-tenant data confusion/impersonation: a handler that keys any decision or persisted data on the webhook's `shop` value can be tricked into attributing actions to, or acting on behalf of, a shop that never sent the corresponding event. Depending on how a given app's `WebhookHandler#handle` uses `data.shop` (e.g., to fetch/activate a session, gate mandatory GDPR redact/data-request compliance flows, or update per-shop billing/subscription state), this can escalate to acting with another tenant's identity — matching the "cross-tenant access" High-impact category.

### Likelihood Explanation
Exploitation requires the attacker to possess one valid `(body, hmac)` pair produced under the target app's `api_secret_key`. Because the same secret signs webhooks for every shop that installs the app, and any developer/attacker can install their own test/dev instance of a public or public-ish app to receive at least one legitimately signed webhook, obtaining such a pair is realistic without needing the victim's credentials. Replaying it against the app's public webhook endpoint with a spoofed `shop-domain` header requires no special access — only network access to the endpoint, matching "unprivileged internet user."

### Recommendation
Bind the `shop` (and ideally `topic`, `api-version`, `webhook-id`) into the value that is actually verified, rather than trusting them as separate, unauthenticated headers. Concretely, have `Request#to_signable_string` incorporate the tenant/topic headers (as Shopify's HMAC scheme intends the raw body to be tied 1:1 to a specific delivery for a specific shop via Shopify's own signing), or have `Registry.process`/consuming apps cross-check `request.shop` against an independently trusted source (e.g., a shop that is already known/authorized in app storage) before dispatching to the handler, and document that consumers must not treat `shop` as authenticated by the HMAC alone.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and captures one legitimate webhook delivery: raw body `B` and its valid header `x-shopify-hmac-sha256: H` (computed by Shopify using the app's `api_secret_key`).
2. Attacker sends a POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid since it only signs `B`), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`= B`) and matches `H` — validation passes [6](#0-5) .
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, even though the event never originated from the victim shop [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-23)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
```
