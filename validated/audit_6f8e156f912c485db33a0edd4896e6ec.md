Confirmed: `Registry.process` only validates the HMAC over `request.to_signable_string` (which returns `@raw_body`), then unconditionally trusts `request.shop` — parsed straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header — to build `WebhookMetadata` and dispatch to the handler.This confirms the gem's documented contract: `Registry.process` docstring explicitly states it "will verify the request did indeed come from Shopify" (docs/usage/webhooks.md:125), and the handler is expected to trust `data.shop` as "the shop domain of the webhook" (docs/usage/webhooks.md:14). The actual verification only covers `@raw_body`, not the shop-domain header, so this is a genuine gap between what's documented/trusted and what's cryptographically verified.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop-attribution spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's HMAC using only the raw request body as the signable content, while the `shop` value it hands to the app's handler is read from an unauthenticated header. An attacker who possesses one genuine `(raw_body, hmac)` pair (trivially obtainable by installing the target app on their own free/test shop and receiving a real webhook) can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. The HMAC check still passes because the header is not part of the signed content, so the handler executes attacker-supplied webhook data attributed to a shop the attacker does not control.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is parsed directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` performs HMAC validation and then, if it passes, unconditionally forwards `request.shop` to the handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac` header: [4](#0-3) 

The identity binding that should hold is: `shop_header == shop_that_produced(raw_body, hmac)`. Because `shop` is excluded from the signable string, this equality is never checked — any `shop` header value is accepted as long as the body/HMAC pair is valid for *some* shop using the app's shared secret. The documentation instructs handlers to trust `data.shop` as "the shop domain of the webhook" without any caveat that it is unauthenticated, reinforcing that this is expected/relied-upon behavior of the gem's public API, not a host-app misuse.

### Impact Explanation
This breaks the tenant-identity binding for webhook processing. A handler that uses `data.shop` to decide which merchant's data to update, delete, or overwrite (as the documented example does — `perform_later(shop_domain: data.shop, webhook: data.body)`) can be tricked into applying attacker-controlled webhook payloads to a victim shop's tenant context, since the gem's own verification API reports the request as valid. This is a cross-tenant attribution/confusion vulnerability rooted entirely in this gem's `Request`/`Registry`/`HmacValidator` implementation, not in host-application misuse of a documented safeguard — the gem provides no shop-binding safeguard to bypass.

### Likelihood Explanation
The prerequisite — a genuine `(raw_body, hmac)` pair signed with the app's secret — is attainable by any unprivileged internet user: they can install the target public app on a free Shopify development store they control, trigger a real event (e.g., create an order), and capture the resulting webhook delivery (body + `hmac-sha256` header) that Shopify sends to the app's public endpoint. They then POST that identical body and HMAC directly to the same public webhook endpoint with a different `shopify-shop-domain` header value. No access token, `client_secret`, or privileged account is required.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-covered signable content, or otherwise cryptographically bind `request.shop` to the verified payload before it is exposed to handlers — e.g., derive/verify shop attribution from a signed claim rather than a bare header, or require the host app to cross-check `data.shop` against a known/allowlisted set of installed shops before trusting it. At minimum, update `Registry.process`/documentation to make explicit that `data.shop` is not authenticated by the HMAC check and must not be treated as a trusted tenant identifier on its own.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g. `orders/create`) and captures the real delivery: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid HMAC of `B` under the app's `api_secret_key`), `x-shopify-shop-domain = attacker-shop.myshopify.com`.
3. Attacker POSTs to the same public webhook endpoint (e.g. `/callback/orders/create`) with body `B`, header `x-shopify-hmac-sha256 = H` unchanged, but `x-shopify-shop-domain = victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds successfully; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H` — validation passes. [5](#0-4) 
5. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and `body` fully controlled by the attacker, and performs its documented action (e.g. `perform_later(shop_domain: data.shop, webhook: data.body)`) against the victim tenant. [6](#0-5)

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
