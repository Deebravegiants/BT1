## Finding

### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but its `to_signable_string` returns only the raw request body, while the shop identity (`shop-domain` header) used downstream by `Webhooks::Registry.process` is read directly from an unauthenticated HTTP header and is never included in the HMAC-signed payload.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

Note that `to_signable_string` returns only `@raw_body`. Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies the `hmac` field against `to_signable_string` (i.e., the raw body) using the app's shared `api_secret_key`: [3](#0-2) 

`Webhooks::Registry.process` then trusts the header-derived `shop` and forwards it, unverified, to the handler as the tenant identity: [4](#0-3) 

The identity-binding equality that should hold is: `shop that HMAC authenticates == shop the handler acts on`. Here, the HMAC authenticates only the raw body content against the app's `client_secret`, but says nothing about which shop the body belongs to — that binding is asserted solely by an attacker-controllable header.

Because a Shopify app's `client_secret` (used to sign all webhooks) is shared across every shop that has the app installed, any merchant who legitimately installs the app receives real webhooks with a valid HMAC over their own body. That merchant can capture one such `(raw_body, hmac)` pair from their own shop and replay it to the app's webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (the body/HMAC pair is untouched and genuinely signed by Shopify for that body), yet `Registry.process` reports the forged `shop` to the handler.

### Impact Explanation
Applications built on this gem use `WebhookMetadata#shop` to determine which tenant's data or session the webhook event applies to (e.g., to look up the shop's session/access token, update the shop's local records, or trigger tenant-specific side effects). Because `shop` is not bound by the HMAC, any existing app-installer can inject arbitrary attacker-chosen body content that is attributed to a different, victim shop of their choosing — a cross-tenant data/write confusion that breaks tenant isolation, one of the explicitly in-scope Critical impacts (cross-tenant access).

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate merchant who has installed the target app (a low bar — anyone can install an app on their own dev/test store) and the ability to POST an HTTP request with a modified header to the app's public webhook endpoint. No access to the app's `client_secret`, session, or victim credentials is needed. Since `shop-domain` is a plain header (not covered by the HMAC), forging it is trivial.

### Recommendation
- Bind the shop identity to the HMAC-verified payload rather than the raw header alone, e.g., have `to_signable_string` include the `shop`, `topic`, and `webhook_id` alongside the body, or validate that `request.shop` corresponds to a shop for which the app maintains an active, previously-established session before trusting `WebhookMetadata#shop`.
- At minimum, document (and enforce in `Registry.process`) that consumers must independently verify `request.shop` is a shop with a currently valid installation/session before acting on the webhook payload, rather than treating the header as authenticated data.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and subscribes to a webhook topic (e.g., `orders/create`).
2. Shopify delivers a webhook: body `B`, header `x-shopify-shop-domain: attacker.myshopify.com`, and `x-shopify-hmac-sha256: HMAC(client_secret, B)`.
3. Attacker resends the identical body `B` and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(client_secret, B)` against the unchanged body `B` (see `to_signable_string` returning `@raw_body` only) — see `lib/shopify_api/webhooks/request.rb#L35-L38` and `lib/shopify_api/utils/hmac_validator.rb#L12-L22`.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: attacker-controlled JSON, ...)` (`lib/shopify_api/webhooks/registry.rb#L198-L199`), causing the app to process attacker-controlled data under the victim shop's identity.

### Citations

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
