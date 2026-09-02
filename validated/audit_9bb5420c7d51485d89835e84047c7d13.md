Confirmed: the documented processing flow explicitly tells apps to trust `data.shop` from `WebhookMetadata` as the tenant identifier for downstream work (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), while `ShopifyAPI::Webhooks::Registry.process` only checks `Utils::HmacValidator.validate(request)`, which signs solely `@raw_body` [1](#0-0) . This confirms the binding break I found.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant spoofing of webhook shop identity - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature Shopify computes covers exclusively the JSON body. `ShopifyAPI::Webhooks::Registry.process` verifies that HMAC but then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id`, all of which are read straight from unauthenticated HTTP headers, and forwards them to the app's handler as `WebhookMetadata` [2](#0-1) . This breaks the identity binding `hmac_signed_bytes == tenant_identifying_bytes`: the bytes that are cryptographically verified (body only) are not the bytes the app uses to determine which shop/tenant the webhook belongs to (the `shop-domain` header).

### Finding Description
`Request#hmac`, `#topic`, `#shop`, `#api_version`, and `#webhook_id` are all derived from HTTP headers [3](#0-2) , whereas `#to_signable_string` (the value actually HMAC-verified) returns only `@raw_body` [1](#0-0) . `Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(..., secret, signable_string)` and compares it to the received `hmac` header using `OpenSSL.secure_compare` [4](#0-3) . Because the signable string never includes `shop-domain`, `topic`, or `webhook_id`, a valid signature for a given body remains valid no matter what values an attacker puts in those headers.

`Registry.process` uses exactly this unauthenticated `shop` value to build the `WebhookMetadata` struct handed to the app's handler [2](#0-1) , and the gem's own documentation instructs apps to treat `data.shop` as "The shop domain of the webhook" and use it directly for tenant-scoped processing (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [5](#0-4) . The equality that should hold — "the shop whose secret validated this request" == "the shop the app attributes this data to" — is broken, because the shop identity is parsed from bytes that are never part of the verified signature.

Because Shopify apps use a single `api_secret_key` shared across all merchant installations of the app (not a per-shop secret), any unprivileged internet user who installs the public app on their own store legitimately receives real webhook deliveries with a valid HMAC over a body they fully control the shape of. They can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still passes (it never looked at the header), `Registry.process` finds a handler for the (also attacker-controlled) `topic` header, and the app processes attacker-supplied body content as if it originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who is a legitimate (but unprivileged) tenant of the app can make the app attribute arbitrary webhook content to a different, victim shop. Any host application logic that keys off `WebhookMetadata#shop` for authorization, data storage, or triggering shop-scoped side effects (exactly as documented) can be tricked into applying attacker-controlled data/topic to another tenant's records, which matches "cross-tenant access."

### Likelihood Explanation
Medium-to-High: the only prerequisite is that the attacker has legitimately installed the app on their own store (a routine, unprivileged action for any public Shopify app), giving them a valid `(body, hmac)` pair for the shared secret. No access token, `client_secret`, or privileged credential is required — they only replay an HTTP POST with substituted headers.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook_id`/`api_version`) in the signed material, or otherwise cryptographically bind them to the verified request, before trusting `request.shop`/`WebhookMetadata#shop` for tenant attribution. At minimum, document and/or enforce that consumers must cross-check `data.shop` against a shop they already know has this webhook/app installed (e.g., validate against their own session store) rather than trusting it as an authenticated value on its own.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and lets the app register webhooks; Shopify delivers a webhook with a known JSON body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker crafts a new POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs `B`)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
   - Header `X-Shopify-Topic`: any registered topic
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and matches `H` — validation passes [6](#0-5) .
4. The app's handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` [7](#0-6)  and processes/persists it as if it were a legitimate webhook for `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L12-30)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
