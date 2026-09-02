### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to identify which tenant the event belongs to. Because the app's `api_secret_key` is shared across every shop that has installed the app, any shop that has a live installation can produce a validly-signed webhook body and then relabel it with a different shop's domain, breaking the binding between "shop whose HMAC was verified" and "shop the handler is told to act on."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the (unsigned) header and is never mixed into the signable string: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately hands `request.shop` to the handler as the tenant identity, with no additional check that the header matches the shop the body actually originated from: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` only compare the digest of `to_signable_string` (i.e. the raw body) against the `hmac` header, using the single, app-wide `Context.api_secret_key`: [4](#0-3) [5](#0-4) 

The identity binding that should hold is:
`shop authenticated by HMAC == shop acted on by the handler`

But since the HMAC is computed only over the body (not the shop header) and the secret is identical for every shop that installed the same app, this reduces to:
`shop authenticated by HMAC == "any shop that installed this app"`
while
`shop acted on by the handler == attacker-controlled x-shopify-shop-domain header`

An attacker who has installed the app on their own store (a legitimate, unprivileged action available to anyone) can capture one genuinely Shopify-signed webhook delivery for their own shop, then replay that exact body (with its valid HMAC unchanged) to the app's webhook endpoint while substituting `x-shopify-shop-domain` (or `shopify-shop-domain`) with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds because it only checks the body/HMAC pair, and `Registry.process` dispatches the handler with `WebhookMetadata.new(... shop: request.shop ...)` set to the forged victim domain.

### Impact Explanation
This crosses a tenant boundary using a credential that is shared per-app rather than per-shop: any application built on this gem that uses `request.shop` inside its webhook handler (e.g., to look up the tenant record, invalidate a cache entry, write data, or trigger a business action) can be made to perform that action against an arbitrary victim shop's tenant record instead of the attacker's own shop, purely by controlling HTTP headers on a replayed, still-validly-signed body. This is a cross-tenant access primitive achieved without ever possessing the victim's credentials or access token, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple/public merchants: no credentials beyond a normal app installation (something any unprivileged internet user can do by installing the app on their own free/dev store) are needed, and no cryptographic secret needs to be broken — only body/HMAC pairs need to be replayed with modified headers, which is trivial to script.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the verified request to the specific tenant, before using `request.shop` for any tenant-scoped action:
- Prefer verifying the webhook against a per-shop secret / session record (e.g., looking up the installed shop's session by `request.shop` first, and rejecting if no active installation exists for that domain) rather than trusting the header at face value once the app-wide HMAC passes.
- At minimum, document loudly (and ideally enforce in `Webhooks::Registry.process`) that consuming applications must not treat `request.shop` as authenticated merely because `HmacValidator.validate` returned true, and must independently confirm the shop has an active session/installation before acting on the payload.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged flow).
2. Shopify sends a legitimately HMAC-signed webhook to the app's endpoint:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of raw body under the app's shared api_secret_key>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   ```
3. Attacker captures the raw body + `x-shopify-hmac-sha256` value and replays it to the same endpoint, only changing the header:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same valid HMAC, body unchanged>
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Request.new` parses this successfully; `Utils::HmacValidator.validate` returns `true` because it only checked `@raw_body` against the HMAC (see `lib/shopify_api/utils/hmac_validator.rb:26-31` and `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)` (`lib/shopify_api/webhooks/registry.rb:188-199`), causing the app to act as if this event genuinely originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
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
