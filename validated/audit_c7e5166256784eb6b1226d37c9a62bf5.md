This confirms `WebhookMetadata#shop` is a top-level tenant identifier field passed straight to the host app's handler, but it is never part of the signed payload.

### Title
Webhook shop-domain (and topic/id/api_version) headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` (and `topic`/`webhook_id`/`api_version`) values used to attribute the event to a tenant are read from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: `def to_signable_string; @raw_body; end` [1](#0-0) . `HmacValidator.validate` computes and compares the signature strictly against this signable string: `computed_signature = compute_signature(verifiable_query.to_signable_string, secret)` [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values are pulled directly from the (attacker-settable) HTTP headers with no cryptographic binding to the signed body: `def shop; T.cast(shopify_header("shop-domain"), String); end` [3](#0-2) .

`Registry.process` validates only the HMAC of the request, then immediately forwards the unauthenticated `shop` field to the host application's handler as the tenant identity: `raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)` followed by `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))` [4](#0-3) . `WebhookMetadata#shop` is documented and typed as the authoritative tenant field passed to `WebhookHandler#handle` [5](#0-4) .

The identity binding that should hold is: `shop header == shop cryptographically bound to the signed payload`. Because the HMAC only covers `@raw_body`, this equality is never enforced — the `shop-domain` header can be swapped freely for any body+HMAC pair without invalidating the signature.

### Impact Explanation
Because the app's webhook signing secret (`api_secret_key`) is shared across every shop that installs the app (it is not per-tenant), any merchant who legitimately installs the app can trigger real webhook deliveries to their own callback URL and thereby obtain a body+valid-HMAC pair signed with the shared secret. That attacker can then resend the exact same raw body and HMAC header to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header with a victim shop's domain. `Registry.process` will validate successfully (the body/HMAC pair is genuine) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop. Any host application that uses this `shop` field to look up tenant records, update per-shop state, or authorize per-shop actions will act on forged cross-tenant data — this is a cross-tenant confusion/spoofing vector, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any internet user who can install the app on a shop they control (a normal, unprivileged onboarding flow requiring no special access) can generate arbitrarily many valid body/HMAC pairs and then freely relabel the `shop-domain` header when POSTing to the public webhook endpoint. No access token, `client_secret`, or privileged account is required — only the gem's documented `Registry.process` behavior is exercised.

### Recommendation
Bind the tenant/topic identity into the verified payload rather than trusting raw headers post-hoc: e.g. require host applications to independently confirm that `request.shop` corresponds to a shop for which the specific delivery was expected (correlate against a per-shop webhook secret, a stored subscription id, or verify the shop against known installed-shop records) before trusting it, and/or document prominently that `shop`/`topic`/`webhook_id` are unauthenticated fields that must not be used as a sole tenant-authorization key. Ideally, extend the signable string or provide a companion verified-shop lookup so `Registry.process` cannot be tricked into misattributing a validly-signed body to an arbitrary shop.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, obtaining legitimate webhook deliveries signed with the app's single shared `api_secret_key`.
2. Attacker captures a delivery: raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed as `HMAC-SHA256(api_secret_key, B)`), per `HmacValidator.compute_signature` [6](#0-5) .
3. Attacker POSTs body `B` with header `H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and any desired `X-Shopify-Topic`).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [7](#0-6) .
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and, if the host app trusts this `shop` value for tenant-scoped updates, processes attacker-controlled data under the victim's tenant identity.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L27-31)
```ruby
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
