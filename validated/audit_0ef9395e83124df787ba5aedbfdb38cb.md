This confirms the vulnerability: the gem's own documentation (`docs/usage/webhooks.md`) explicitly instructs developers to trust `data.shop` from the processed webhook as "The shop domain of the webhook" — the gem presents `Registry.process` as the complete verification mechanism ("This will verify the request did indeed come from Shopify"), while `request.shop` is read straight from an HTTP header that is never included in the HMAC-signed bytes.I have sufficient evidence to confirm the finding. Presenting the analysis now.

### Title
Webhook shop-domain header is trusted for tenant identification without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies only that the raw request body matches an HMAC computed with the app's `api_secret_key`. The `shop` value that identifies which tenant the webhook belongs to is read directly from the `x-shopify-shop-domain` HTTP header, which is not part of the HMAC-signed material. This breaks the identity binding `hmac_verified_bytes == tenant_identifying_bytes`, letting anyone who can produce (or replay) one valid `(body, hmac)` pair for the shared app secret relabel it as belonging to an arbitrary shop.

### Finding Description
`Utils::HmacValidator.validate` computes the signature strictly over `verifiable_query.to_signable_string`, and for webhooks that method returns only the raw body: [1](#0-0) [2](#0-1) 

`Request#shop` is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic tie to the body or the HMAC: [3](#0-2) 

`Registry.process` validates the HMAC and then forwards `request.shop` verbatim into `WebhookMetadata`, which the host app's handler is told (via the gem's own docs) can be trusted as "The shop domain of the webhook": [4](#0-3) [5](#0-4) 

Since the `api_secret_key` is a single per-app secret shared across every installed shop (not shop-specific), any attacker who has ever received (or can otherwise obtain) one valid `(raw_body, hmac)` pair signed by that app's secret — e.g., by installing the app themselves on their own shop and capturing the webhook Shopify sends them — can resend the identical body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still pass because it never inspects the shop header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This crosses a tenant boundary: an unprivileged user (any attacker who can self-install the app or otherwise obtain one valid signed payload) can make the host application process attacker-controlled webhook data under a victim shop's identity. Depending on how the host app's handler uses `data.shop` (e.g., to look up the victim's session/access token and perform actions, or to write attacker data into the victim's per-tenant records), this enables cross-tenant data injection/corruption — satisfying the Critical "cross-tenant access" impact category, since the shop-scoping guarantee the gem is supposed to provide is broken at the library layer.

### Likelihood Explanation
Likelihood is non-trivial but requires effort: the attacker needs at least one legitimately signed `(body, hmac)` pair, which is trivially obtainable by installing the target's public app on an attacker-controlled shop and capturing the resulting webhook delivery to their own endpoint (or intercepting one's own webhook traffic), then replaying it against the shared webhook endpoint with a forged `shop-domain` header. No access to the app's `client_secret` or a victim's access token is required — only reuse of a signature that was never bound to shop identity in the first place.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed material, or otherwise cryptographically bind them, e.g. by having `Request#to_signable_string` incorporate `shop-domain` alongside the raw body, and reject any request whose header-declared shop does not match a value derivable from the signed payload. Documentation in `docs/usage/webhooks.md` should also be updated to state clearly that `data.shop` is not authenticated by the HMAC and must be independently corroborated (e.g., checked against a known/installed shop) before being trusted for tenant-scoped operations.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop "attacker.myshopify.com"
#    and receives a legitimate webhook, capturing:
raw_body = '{"id":1,"note":"hello"}'
hmac_b64 = "<value from x-shopify-hmac-sha256 header of the real webhook>"

# 2. Attacker replays the identical body+hmac to the same webhook endpoint,
#    but swaps the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => hmac_b64,          # unchanged, still verifies against raw_body
  "x-shopify-shop-domain"  => "victim.myshopify.com", # forged, not covered by HMAC
  "x-shopify-webhook-id"   => "any-id",
  "x-shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# 3. HmacValidator.validate(request) succeeds because it only checks raw_body
#    against the shared api_secret_key -- the forged shop header is never checked.
ShopifyAPI::Webhooks::Registry.process(request)
# => Handler#handle receives WebhookMetadata with shop: "victim.myshopify.com",
#    despite the payload actually originating from the attacker's own shop.
```

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
