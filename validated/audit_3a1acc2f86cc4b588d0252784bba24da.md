### Title
Webhook `shop-domain` Header Not Bound to HMAC Signature Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, but the `shop` value passed on to the app's handler is read from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, which is never included in the signed bytes. Anyone able to produce a body+HMAC pair for their own shop (any merchant that installs the app can trigger webhooks aimed at themselves) can attach that valid body/HMAC to a forged `shop-domain` header naming a different tenant, and the gem will accept it as authentic for the victim shop.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string`, computed with the app's `client_secret`: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only the raw JSON body, and `hmac` is derived only from the `hmac-sha256` header — `shop` is read from a completely separate, unsigned header: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC (body integrity/authenticity of the *body*) and then immediately trusts `request.shop` — a header value that was never covered by that signature — to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

`WebhookMetadata.shop` is the tenant identifier the host application is documented to rely on for routing/persisting webhook data per-shop: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `hmac-signed-bytes == bytes that determine which tenant (shop) the payload is attributed to`. Here that equality is broken: the signed bytes are `raw_body` only, while the tenant attribution comes from an out-of-band, unauthenticated header (`shop-domain`). Because the app's `api_secret_key`/`client_secret` is shared across all shops that install the app (it is not shop-specific), any legitimate merchant using the app can generate a validly-HMAC'd webhook body for their own store (by performing an action that fires a webhook, e.g. creating an order), capture that raw body + HMAC header, and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop that also uses the same app. `Utils::HmacValidator.validate` will still return true because the signature only covers the body, and `Registry.process` will hand the handler `WebhookMetadata` claiming the payload belongs to the victim shop.

### Impact Explanation
This is a cross-tenant boundary violation: an unprivileged attacker (any merchant/installer of the multi-tenant app, or anyone who can capture one valid webhook body+HMAC) can inject attacker-controlled webhook data attributed to an arbitrary other shop that installed the same app. Depending on how the host app's webhook handler uses `data.shop` (persisting order/customer/product changes, triggering per-tenant business logic, cache invalidation, billing events, etc.), this enables cross-tenant data corruption or forced processing of attacker-chosen data under another merchant's identity — matching the "cross-tenant access" high/critical impact class from an identity-binding failure, analogous to the reported `userMaxAllc`/`maxAllocation` mismatch where the wrong entity was bound to the check.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment where the webhook endpoint is public (as documented) and the same `api_secret_key` is used for all shops of the app (the standard, documented multi-tenant model for this gem — see `Context.api_secret_key` usage in `HmacValidator` and `Oauth`). The attacker only needs to be a legitimate (even free-trial) installer of the target app to obtain one valid signed body, and standard HTTP tooling to replay it with a modified header — no access token, `client_secret`, or privileged credentials of the victim are required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is authenticated, not just the raw body. Concretely:
- Compute/verify the HMAC over a signable string that also incorporates the `shop-domain` header (and other headers used for routing), or
- After validating the HMAC, cross-check `request.shop` against an expected/known shop associated with the specific installation context (e.g., require the caller to supply the expected shop and compare), rather than trusting the header value as ground truth.

### Proof of Concept
1. Attacker installs the target multi-tenant app on their own store `attacker.myshopify.com` (a normal, unprivileged install).
2. Attacker performs an action that triggers a subscribed webhook (e.g., updates an order), producing a request with a body `B` and a valid `x-shopify-hmac-sha256` header `H = HMAC(client_secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker intercepts/replays this request to the app's public webhook endpoint but changes the header to `x-shopify-shop-domain: victim.myshopify.com`, keeping `B` and `H` unchanged.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and matches `H` — validation succeeds, per [7](#0-6) .
5. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: B, ...)`, per [8](#0-7) , and processes attacker-controlled data as if it originated from the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
