### Title
Webhook shop-domain identity is not bound by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before dispatching to the app's handler, but the HMAC signature only covers the raw request body. The `shop` identity attached to the verified payload is read from an unauthenticated header and is never bound to the signature, allowing an attacker who owns any Shopify store to relabel a legitimately-signed webhook body as belonging to an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is not part of that signed string: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which internally calls `request.to_signable_string` (body only) and `request.hmac`, then immediately trusts `request.shop` to build the data passed to the app-defined handler: [3](#0-2) [4](#0-3) 

The gem's own documentation states this call "will verify the request did indeed come from Shopify," implying the whole request (including tenant identity) is authenticated: [5](#0-4) 

This breaks the identity binding: `hmac_valid_for(body) == true` is treated as equivalent to `shop_header == originating_shop`, but the two are independent fields — the HMAC only proves the body was produced with the app's shared `client_secret` for *some* legitimate webhook, not that the accompanying `shop` header matches the shop that produced that body.

### Impact Explanation
An attacker who legitimately installs the target app on their own (attacker-controlled) shop can capture a real, correctly-HMAC-signed webhook (e.g. `orders/create` with attacker-chosen order content), then replay the exact `raw_body` + `hmac` header to the app's webhook endpoint while substituting the `shop-domain` header with a victim merchant's domain. `HmacValidator.validate` still passes (it never inspects `shop`), so `Registry.process` calls the handler with `WebhookMetadata.shop` set to the victim's domain and `body` fully attacker-controlled. Any host application that uses `data.shop` from `WebhookMetadata` to key per-tenant database writes, inventory updates, order records, or job dispatch (exactly as shown in this gem's own documented example, `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) will attribute attacker-controlled data to another merchant's tenant — a cross-tenant data-integrity/confidentiality breach reachable by any unprivileged user who can install the app on their own store, without needing the app's `client_secret`, an access token, or any privileged account.

### Likelihood Explanation
Likelihood is high for any app that follows the gem's documented pattern verbatim: any internet user can self-install a Shopify app that supports installation from any store, trigger a webhook-generating action in their own shop to obtain a validly signed body/HMAC pair, and then send a forged HTTP request to the app's public webhook endpoint with the `shop-domain` header swapped. No credentials, secrets, or elevated privileges are required beyond ordinary access to one's own merchant account.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signed material, or independently authenticate the shop domain against the app's known set of legitimately-installed/authorized shops before invoking the handler. At minimum, `ShopifyAPI::Webhooks::Registry.process` should not imply to consumers (via docs or API contract) that `request.shop` has been authenticated — that field is currently attacker-controlled and unbound to the HMAC.

### Proof of Concept
1. Attacker installs the vulnerable app on their own store `attacker.myshopify.com` and triggers a webhook, e.g. `orders/create`, capturing the raw POST including headers `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker.myshopify.com`, and body `raw_body`.
2. Attacker resends an HTTP POST to the app's webhook route with the identical `raw_body` and identical `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. The app calls `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers))`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only (via `to_signable_string`) and it matches, so validation passes: [6](#0-5) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-controlled `body`, and the host app (following the gem's documented pattern) processes/persists this data under the victim tenant's identity.

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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
