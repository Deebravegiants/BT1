### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` binds its HMAC signature to the raw request body only, while the `shop` (and `topic`/`webhook_id`) values are taken verbatim from unauthenticated HTTP headers. `Webhooks::Registry.process` validates the HMAC and then forwards the unauthenticated `shop` value straight to the app's webhook handler. Because the HMAC secret (`Context.api_secret_key`) is shared across every shop installed on the app, a valid `(body, hmac)` pair captured from one tenant's webhook can be replayed with a different `x-shopify-shop-domain` header and will still pass validation, causing the host application to process the payload under the wrong shop's identity.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` (and `topic`, `webhook_id`, `api_version`) are read directly from headers, which are never part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., over the body only) and, once it passes, hands the caller-supplied `request.shop` straight to the registered handler as trusted identity metadata: [3](#0-2) 

`HmacValidator.validate` computes/compares the signature purely against `verifiable_query.to_signable_string`, which for a webhook `Request` is the body — it never incorporates the `shop` header: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:
`shop_bound_by_hmac_signature == shop_header_trusted_by_handler`

Before the attack: a legitimate webhook for shop A arrives with body `B`, `hmac = HMAC(secret, B)`, and header `x-shopify-shop-domain: shop-a.myshopify.com`. `HmacValidator.validate` passes because `HMAC(secret, B)` matches.

Attacker action: any merchant who has installed the app on shop A can trigger a real webhook for shop A (e.g. `orders/create`), capture the exact `(body, hmac)` pair Shopify sent to the app, and replay it to the app's webhook endpoint while substituting `x-shopify-shop-domain: shop-b.myshopify.com` (a target victim shop also installed on the same app, whose domain can be enumerated/guessed).

After the attack: body `B` and `hmac` are unchanged, so `HmacValidator.validate` still returns true (it only checks the body). `Registry.process` then builds `WebhookMetadata.new(topic:, shop: "shop-b.myshopify.com", body: parsed_body, ...)` and invokes the host app's handler — which will typically use `shop` to look up the tenant's session/record and apply `body`'s data to shop B's data store, even though the data actually originated from shop A.

Because `api_secret_key` is one shared secret for the whole app across all installed shops, this signature scheme provides no per-tenant binding, and this gem provides no mechanism (e.g., binding shop into the signable string, or requiring the caller to cross check the header shop against session storage) to prevent this cross-tenant misattribution.

### Impact Explanation
This is a cross-tenant identity confusion: the webhook payload legitimately signed for shop A is accepted and processed as if it belongs to shop B. Depending on the handler, this can lead to writing or triggering business logic for the wrong merchant's tenant (e.g., an `orders/create` payload being recorded against another shop, or a `app/uninstalled` handler tearing down the wrong tenant's data) — this matches the "cross-tenant access" Critical impact category in scope.

### Likelihood Explanation
The only requirement is that the attacker controls at least one shop with the app installed (any unprivileged merchant/user can install a public app) and can send raw HTTP requests to the app's public webhook endpoint with attacker-chosen headers — no access token, `client_secret`, or privileged account is required. Capturing one's own legitimate webhook body+HMAC is trivial (e.g., via logging, a proxy, or a debug endpoint), and the victim shop domain is often discoverable (installed apps commonly expose shop domains via public URLs/redirects).

### Recommendation
Bind the shop identity into the value that is actually verified by the HMAC, rather than trusting an unauthenticated header:
- Change `Request#to_signable_string` (or `HmacValidator`) so the shop domain (and other identity-bearing headers used by the handler) are included in the signed payload, or
- Require handlers/`Registry.process` to independently confirm that `request.shop` corresponds to a shop that legitimately owns the delivered `webhook_id`/subscription (e.g., cross-check against stored webhook registrations per shop) before dispatching to the handler.

### Proof of Concept
```ruby
# Attacker has installed the app on shop-a.myshopify.com and captured a legitimate webhook delivery:
body = '{"id":123,"total_price":"10.00"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)

# Attacker replays the exact same body/hmac but swaps the shop-domain header to a victim shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "shop-b.myshopify.com", # victim, not the shop that generated this webhook
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)

# This succeeds because the HMAC only covers `body`, not the shop header:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata(topic: "orders/create", shop: "shop-b.myshopify.com", body: {...}))
# The host app now believes this order payload belongs to shop-b, not shop-a.
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
