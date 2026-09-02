Based on the analysis, this maps to a concrete identity-binding break in the webhook processing path.

### Title
Webhook `shop-domain` header is trusted without HMAC coverage, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` covers **only** the JSON payload — never the `shop-domain`, `topic`, or `webhook-id` headers. `Registry.process` nonetheless takes `request.shop` straight from that unauthenticated header and hands it to the app's handler as the tenant identifier (`WebhookMetadata#shop`). The binding the gem should enforce — *shop cryptographically bound to the signed payload* == *shop the handler treats as the authenticated tenant* — does not hold.

### Finding Description
`lib/shopify_api/webhooks/request.rb` computes the signable string as: [1](#0-0) 
and exposes `shop` purely from the header: [2](#0-1) 

`Registry.process` validates the HMAC of the body only, then immediately trusts `request.shop` for dispatch: [3](#0-2) 

Because the app's webhook secret (`Context.api_secret_key`) is shared across every shop that installs the app (it is not per-shop), any merchant who installs the app can legitimately trigger a webhook delivery for their own store and obtain a body + valid HMAC pair. That attacker-controlled shop can then replay the exact same body/HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looks at headers), and `Registry.process` forwards `data.shop = <victim shop>` to the app's handler — a cross-tenant identity confusion where the "authenticated" shop (the one whose HMAC secret produced the signature) is not the shop asserted to the handler.

### Impact Explanation
This breaks tenant isolation: the receiving application will process/store the replayed payload as though it originated from the victim's store. Depending on how the host app's `WebhookHandler` uses `data.shop` (e.g., to look up records, update local per-shop state, or as a key into a merchant's data store, as shown in the gem's own documented usage pattern `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), an attacker can inject/forge data attributed to another merchant's tenant using only their own legitimately-obtained webhook credentials — a cross-tenant access outcome.

### Likelihood Explanation
Likelihood is high for any app author following the gem's documented pattern verbatim (`docs/usage/webhooks.md`), since the gem provides no protection against header/shop spoofing beyond body HMAC verification, and shop domain values are entirely attacker-suppliable HTTP headers. The only prerequisite is that the attacker has (or creates) an app installation on their own store to obtain one valid signed webhook payload/HMAC pair, which is trivially available to anyone who can install the app (unprivileged in the sense of having no special access to the victim's tenant).

### Recommendation
Bind the shop to the signature: include the `shop-domain` (and ideally `topic`/`webhook-id`) header value in `to_signable_string`, or otherwise cryptographically bind the shop to the payload before verification, so that changing the `shop-domain` header invalidates the HMAC. At minimum, `Registry.process` (or the consuming app) should cross-check `request.shop` against an expected/authorized shop set rather than accepting it as ground truth purely because the body-only HMAC passed.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, obtaining a legitimate webhook delivery (e.g. `orders/create`) with headers `shopify-shop-domain: attacker.myshopify.com`, `shopify-hmac-sha256: <valid HMAC of body>`, and body `B`.
2. Attacker replays the exact same raw body `B` and HMAC value to the app's webhook endpoint, but changes the `shopify-shop-domain` header to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: spoofed_headers)` is constructed by the app's controller exactly as documented.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only hashes `B`, not the headers [4](#0-3) .
5. `Registry.process` dispatches `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)` to the handler, which acts on victim's tenant data using attacker-supplied content [5](#0-4) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
