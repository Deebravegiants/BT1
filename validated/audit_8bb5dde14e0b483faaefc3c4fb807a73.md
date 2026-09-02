This confirms the vulnerability path: the gem's documented API explicitly tells app developers to trust `data.shop` (the shop domain) as the tenant identifier for webhook processing [1](#0-0) , and the `WebhookMetadata` struct exposes `shop` as a first-class trusted field [2](#0-1) , while the HMAC signature that `Registry.process` checks is computed only over the raw body, never the `shop-domain` header.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [3](#0-2) , while `shop` is read verbatim from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic binding to the signed payload [4](#0-3) . `Registry.process` validates only this body-based HMAC before dispatching the shop value to the app's handler [5](#0-4) .

### Finding Description
The identity binding that should hold is: `shop-domain (verified by HMAC) == shop-domain (delivered to handler)`. In `Request`, `hmac` is computed over `@raw_body` alone [6](#0-5) [3](#0-2) , and `HmacValidator.validate_signature` compares the received HMAC against a signature computed solely from `to_signable_string` [7](#0-6) . The `shop` header is never part of the signed bytes.

Because the gem's shared secret (`Context.api_secret_key`) is the same across every shop that installs a given app, any merchant who has legitimately installed the app can capture a real, validly-signed webhook delivered to their own endpoint (body + `x-shopify-hmac-sha256`), then replay that exact body/HMAC pair while substituting the `x-shopify-shop-domain` header with a different, victim shop's domain. `Registry.process` still finds `Utils::HmacValidator.validate(request)` true (since the body/HMAC are unchanged) and forwards `shop: request.shop` unaltered into `WebhookMetadata`, attributing the (possibly reused/incorrect) payload to a tenant the attacker doesn't own [5](#0-4) .

This mirrors the report's root cause pattern: a value that participates in a downstream security decision (`shop`, used exactly as the tenant/session key per the gem's own documentation) is not covered by the verification mechanism (HMAC) that is supposed to authenticate the whole request, just as `_deployedAmount` was excluded from the balance-tracking update relied upon by `harvest`.

### Impact Explanation
Per the gem's documented contract, `data.shop` is meant to be the authenticated tenant identifier apps use for dispatching background jobs, storing/loading per-shop sessions, and processing shop-scoped data [1](#0-0) [8](#0-7) . Since the gem itself does not bind `shop` to the HMAC, any application built strictly on this gem's documented API (as shown in its own example) will process attacker-controlled `shop` values as if authenticated, enabling cross-tenant data confusion/injection — this is a Critical-class cross-tenant boundary break rooted entirely in this gem's verification logic, not in host-application misuse.

### Likelihood Explanation
The attacker only needs a normal, unprivileged Shopify store that has installed the target app — no leaked secrets, no access tokens, no privileged account. They passively capture one legitimate webhook delivery to their own endpoint (trivial, as they control that endpoint) and replay it with a modified header. No cryptographic material needs to be broken; the flaw is structural.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook_id`) header values in the HMAC-covered signable string in `ShopifyAPI::Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the shop identity to the verified payload before it is handed to `WebhookMetadata`/handlers.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(client_secret, B)`), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker sends the same `B` and `H` to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`; since validation only checks `HMAC(client_secret, B) == H`, it returns true regardless of the shop header [9](#0-8) .
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` and processes it as if it were an authenticated webhook for `victim-shop`, per the documented handler pattern [10](#0-9) [8](#0-7) .

### Citations

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
