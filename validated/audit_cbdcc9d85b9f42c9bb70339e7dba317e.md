### Title
Webhook `shop` identity used to route tenant data is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request body, then hands the caller a `WebhookMetadata` struct whose `shop`, `topic`, and `webhook_id` fields come from unauthenticated HTTP headers. Because the shared secret used for the HMAC (`Context.api_secret_key` / `client_secret`) is the same for every shop that has installed a given app, any party who can obtain one valid `(body, hmac)` pair for that app can replay the body with a different `shop` header and produce a request that still passes HMAC validation while claiming to originate from a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `hmac`, `topic`, `shop`, `api_version`, and `webhook_id` from HTTP headers, and exposes `to_signable_string` returning only `@raw_body`: [1](#0-0) 

`Registry.process` verifies the request using only that raw body against the HMAC header, then dispatches to the app's handler passing `request.shop`, `request.topic`, and `request.webhook_id` — none of which are covered by the signature: [2](#0-1) 

The HMAC computation itself only ever signs `verifiable_query.to_signable_string`, i.e., the body — never the headers: [3](#0-2) 

`WebhookMetadata` (the object the host application's `WebhookHandler#handle` receives to identify which tenant/session the payload belongs to) is built directly from these unauthenticated header values: [4](#0-3) 

**Broken binding:** `shop` (and `topic`/`webhook_id`) claimed in the HTTP headers ≠ `shop` (and `topic`/`webhook_id`) bound by the HMAC (which covers only the raw body bytes). The `api_secret_key`/`client_secret` used for the HMAC is shared across every shop that has installed the app, not scoped per-shop. Consequently, once *any* valid `(raw_body, hmac)` pair for a given topic is known — e.g., obtained from a webhook the attacker's own store legitimately received after installing the app — that exact body/HMAC pair remains valid when replayed with a `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to a victim shop. `Utils::HmacValidator.validate` will return `true` because it never inspects the shop header, and the host application's handler will process attacker-controlled data under the identity of another tenant.

### Impact Explanation
This crosses a tenant boundary: an app built on this gem cannot distinguish "webhook genuinely sent by Shopify for shop B" from "captured body from shop A's own legitimate webhook, replayed with the shop header swapped to B," because the gem's own signature verification does not bind the header-derived tenant identity to the signed bytes. Depending on how the host app uses `WebhookMetadata#shop` (commonly used to look up the session/store record to act on), this can enable cross-tenant data injection/corruption or triggering of tenant-scoped side effects (e.g., app-uninstall handling, order/customer data processing) under a false shop identity — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any unprivileged party who can install the app on their own store (a normal, unprivileged interaction with any public Shopify app) will receive legitimate webhook deliveries with valid `(body, hmac)` pairs for their own shop. Because the same `client_secret` HMAC is valid across shops and does not bind to `shop`/`topic`, that captured pair can be replayed at the app's public webhook endpoint with an altered shop header. No access token, session, or `api_secret_key` disclosure is required — the attacker only needs a body they were legitimately shown once.

### Recommendation
Bind the identity fields that are acted upon into the signed material, or otherwise independently re-verify them: include `shop`, `topic`, and `webhook_id` in the HMAC-signed payload (as Shopify's own webhook signing conventions could be extended to do), or have `Registry.process` cross-check `request.shop` against session/shop state already known to the host app rather than trusting the header value verified only by a body-only HMAC. At minimum, document to consuming apps that `WebhookMetadata#shop` is not cryptographically bound by `HmacValidator.validate` and must not be trusted as an authenticated tenant identifier on its own.

### Proof of Concept
1. Attacker installs the target app on their own development/test shop (`attacker.myshopify.com`), which is unprivileged and freely available to any Shopify merchant.
2. Shopify sends the attacker's shop a legitimate webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker replays the exact same request to the app's public webhook endpoint, but rewrites `x-shopify-shop-domain` (or `shopify-shop-domain`) to `victim.myshopify.com`, keeping `B` and `H` unchanged.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and compares it to `H` via `OpenSSL.secure_compare` — this succeeds because the body `B` was not modified. [2](#0-1) 
5. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: ...)` and, if the host app looks up the victim shop's session/state using this `shop` value, processes attacker-supplied data as though Shopify had genuinely reported it for the victim tenant.

**Note on confidence:** I was not able to inspect any host-app reference implementation bundled in this repo (e.g., in `docs/usage/webhooks.md`) to confirm exactly how `WebhookMetadata#shop` is typically consumed downstream; the severity depends on that usage, which is outside this gem but is the documented intended purpose of the field.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
