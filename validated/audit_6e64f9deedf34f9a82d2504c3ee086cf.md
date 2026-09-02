### Title
Webhook `shop` identity used by `Registry.process` is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which computes the HMAC over `Request#to_signable_string` — defined as the raw body only. The `shop` field, which the gem's own documentation instructs handler authors to trust as the tenant identifier, is read from the `x-shopify-shop-domain` header and is never included in the signed bytes.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 

`Request#shop` is derived from an HTTP header that is entirely outside that signed string: [2](#0-1) 

`Registry.process` validates the HMAC and, on success, forwards `request.shop` unchanged into `WebhookMetadata`, which the host app's handler is documented to trust as the authoritative tenant/shop identity: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever compare `verifiable_query.to_signable_string` (the body) against the `hmac` header — it has no knowledge of, and does not bind, the `shop` header: [4](#0-3) 

The gem's documentation explicitly tells integrators to key their business logic off `data.shop` from the callback, with no instruction to cross-check it against anything else: [5](#0-4) 

This breaks the identity binding: `hmac == HMAC(secret, raw_body)` says nothing about `shop`, yet the code and the documented usage pattern treat `request.shop` as if it were authenticated by that same HMAC. Concretely: `HMAC-verified(raw_body) ⇒ trusted(shop-domain header)` — an equality the gem does not actually enforce.

### Impact Explanation
An unprivileged internet user who has legitimately installed the app on their own store (Shop A) — a normal, unprivileged tenant with respect to every other merchant's data — receives real Shopify webhooks with a valid `hmac-sha256` header computed only over the JSON body. Because the header set is never part of the signed material, that attacker can replay the exact same `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g., Shop B's domain). `HmacValidator.validate` still returns `true` because it only checks the body/hmac pair, and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen value. Any host application built per this gem's own documented pattern (using `data.shop` to select/mutate the correct tenant's records, e.g. enqueuing background jobs keyed by `shop_domain`) will process or misattribute data under a different, unauthorized shop, i.e., cross-tenant data injection/impersonation — the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High. No secret material beyond what any app installer already legitimately possesses (a valid webhook delivery to their own shop) is required. The attacker doesn't need to forge an HMAC at all — they need only replay a body/hmac pair they legitimately received and swap one unauthenticated header. This requires no credential compromise, no TLS interception, and no social engineering beyond installing the app on the attacker's own store, which is standard, expected usage.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`, `api_version`) to the signed material, or otherwise cryptographically tie the header set to the signature, before it is exposed to the handler:
- Include the shop domain (and other trusted headers) in the string that is HMAC-verified, e.g. by having `to_signable_string` hash `headers + raw_body` rather than `raw_body` alone, and updating validation/documentation accordingly; or
- At minimum, document and enforce that `WebhookMetadata#shop` must be cross-checked by the host application against a shop the app has an active, verified session/installation record for before any tenant-scoped action is taken, and make this a required check inside `Registry.process` rather than leaving it to be discovered by integrators.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook delivery, e.g. for `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC_SHA256(client_secret, B)`.
2. Attacker resends an HTTP request to the app's webhook endpoint with:
   - Body: the same `B`
   - Headers: `x-shopify-hmac-sha256: H` (unchanged), `x-shopify-topic: orders/create` (unchanged), `x-shopify-shop-domain: victim-shop.myshopify.com` (changed)
3. The app constructs `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` and calls `ShopifyAPI::Webhooks::Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC_SHA256(client_secret, B)` and finds it equal to `H` → passes, per `lib/shopify_api/utils/hmac_validator.rb#L12-L31`.
5. `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, per `lib/shopify_api/webhooks/registry.rb#L188-L200`, causing the host app to act on `victim-shop`'s data/tenant scope even though the payload actually originated from `attacker-shop`.

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

**File:** docs/usage/webhooks.md (L12-29)
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
