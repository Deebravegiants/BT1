### Title
Webhook shop identity spoofing via HMAC that only covers the request body, not the `shop-domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body. The `shop` (tenant) identity that is handed to the app's webhook handler is read from an HTTP header that is never included in the HMAC-signed material. Because the `api_secret_key`/`client_secret` used to sign webhooks is a single value shared by the app across every merchant, any unprivileged user who installs the app on their own shop can capture a legitimately-signed `(body, hmac)` pair and replay it with an arbitrary `X-Shopify-Shop-Domain` header, causing the gem to hand a victim shop's identity to the app's webhook handler for attacker-controlled event data.

### Finding Description
`Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) does:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [1](#0-0) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string`, and `Webhooks::Request#to_signable_string` returns exclusively `@raw_body`:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

The `shop` value that gets passed to the handler is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is entirely outside the HMAC computation:

```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [3](#0-2) 

The identity binding that should hold is: `hmac_valid(body) ⇒ shop == originating_shop`. In this implementation the binding is broken: `hmac_valid(body)` only proves "this body was produced with the app's shared secret," it does **not** prove which shop the header claims. Since `api_secret_key` is one value shared by the app across all installed shops (see `ShopifyAPI::Utils::HmacValidator.validate_signature`, which signs/verifies using `Context.api_secret_key` globally, not a per-shop secret) [4](#0-3) , any shop that installs the app can generate a genuinely-valid `(body, hmac)` pair for itself, then re-POST that exact body/HMAC to the app's webhook endpoint while substituting a different value in the `shop-domain` header. `Registry.process` will accept it as valid and dispatch `WebhookMetadata` carrying the attacker-chosen `shop` value to the app's handler.

### Impact Explanation
This is a cross-tenant identity-confusion primitive inside the gem's own webhook verification path: `request.shop`, which apps commonly use to look up/scope per-tenant sessions, state, or data, is unauthenticated relative to the verified content. An attacker (merely by installing the app on their own store — a normal, unprivileged action) can make the library report attacker-controlled webhook data as belonging to any other shop domain string. Depending on how the host app's webhook handler uses `data.shop` (e.g., to fetch a stored session/access token for that shop and act on it, or to write data keyed by shop), this enables cross-tenant data corruption or the attacker's payload being processed under another merchant's identity — a Critical, cross-tenant impact rooted entirely in this gem's `Webhooks::Request`/`Registry` verification logic.

### Likelihood Explanation
High. No privileged credentials, tokens, or secrets belonging to the victim are required. The attacker only needs: (1) their own (attacker-owned) shop installation of the target app to obtain one valid `(raw_body, hmac)` pair, and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header — both trivially available to any internet user targeting an app that uses this gem's `Webhooks::Registry.process` as documented.

### Recommendation
Bind the shop identity into the verified material instead of trusting an unauthenticated header:
- Include the shop domain header value in the HMAC-signable string (`to_signable_string`) so any tampering with `shop-domain` invalidates the HMAC, or
- Cross-check `request.shop` against a shop identity already bound to a specific installed session (e.g., verify the shop is one the app expects for that webhook subscription) before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (fully unprivileged, self-service).
2. Attacker triggers any subscribed webhook topic on their own shop, capturing the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC(api_secret_key, B)` — valid because the app's `api_secret_key` is shared across all shops.
3. Attacker resends the exact same `B`/`H` to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(api_secret_key, B) == H` [5](#0-4) .
5. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "victim-shop.myshopify.com"` [6](#0-5) , and the handler processes attacker-controlled body content under the victim's shop identity.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
