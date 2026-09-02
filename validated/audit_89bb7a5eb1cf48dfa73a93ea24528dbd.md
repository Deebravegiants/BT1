### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authorizes an inbound webhook purely by validating the HMAC over the raw request body, then hands the *unauthenticated* `shop-domain` header straight to the app's handler as the tenant identifier. Because the HMAC only signs the body, an attacker who controls any shop that has the app installed can capture one of their own legitimately-signed webhook deliveries and replay it against the shared webhook endpoint with a forged `shop-domain` header, causing the app to process attacker-supplied data under a victim shop's identity.

### Finding Description
`Registry.process` gates on HMAC validity and then immediately trusts `request.shop`: [1](#0-0) 

The HMAC is verified via `Utils::HmacValidator.validate`, which calls `to_signable_string` on the `Request`: [2](#0-1) 

`Request#to_signable_string` returns only the raw body — none of the headers, including `shop-domain`, are part of the signed material: [3](#0-2) 

Yet `request.shop`, read straight from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header, is the value passed into the handler as the tenant identity: [4](#0-3) [5](#0-4) 

The equality this breaks is:

`shop authenticated by the HMAC` ≠ `shop passed to the handler as WebhookMetadata#shop`

The HMAC only proves *"this body was signed with the app's secret at some point, for some registered shop"*; it proves nothing about which shop the request currently claims to be from. Since every shop installation of a multi-tenant app shares the same webhook callback URL and the same `client_secret`, a webhook body+HMAC pair that is valid for shop A (which the attacker controls, e.g. by placing an order in their own dev/test store to trigger a real `orders/create` webhook) remains HMAC-valid when replayed with the `shop-domain` header changed to shop B. `Registry.process` has no cross-check that ties the signed body to the claimed shop, so it will happily dispatch attacker-controlled webhook data to the handler tagged as coming from shop B.

### Impact Explanation
This is a cross-tenant identity-binding bypass: an attacker who is a legitimate (if unprivileged) merchant installer of the app can inject fabricated webhook events that the host application will attribute to any other shop of their choosing, without ever possessing that shop's credentials or the app's `client_secret`. Depending on how the host app uses webhook data (e.g., updating order/customer records, triggering fulfillment, revoking access on `app/uninstalled`), this enables cross-tenant data corruption, spoofed lifecycle events (e.g., forging an `app/uninstalled` or `shop/redact` event for a victim shop), or injection of attacker-chosen payloads under another tenant's identity — matching the "cross-tenant access" class of Critical impact.

### Likelihood Explanation
Likelihood is high in relative terms among unprivileged findings: it requires no access token, no leaked secret, and no privileged account — only that the attacker be able to install the app on a shop they control (which is a baseline capability of any Shopify app) and can send an HTTP request to the app's shared webhook endpoint with a forged header. Capturing a valid body+HMAC pair from one's own store is trivial and entirely within the attacker's control, and nothing in this gem prevents replaying it with a different `shop-domain` header.

### Recommendation
Bind the shop identity into the signed material, or otherwise verify it out-of-band before trusting `request.shop`:
- Include the `shop-domain` (and ideally `webhook-id`/`api-version`) in the string that is HMAC-verified, not just the raw body, so a mismatched shop invalidates the signature; or
- Have `Registry.process` cross-check `request.shop` against an expected/registered shop for the delivery (e.g., via the `webhook_id`), rejecting the request if there is no independent confirmation that the signed body actually belongs to the claimed shop.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a real event (e.g. places an order), producing a legitimately Shopify-signed webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`, header `x-shopify-shop-domain = attacker.myshopify.com`.
2. Attacker replays this exact `raw_body` and `hmac` header to the app's shared webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` recomputes `HMAC(secret, B)` — unchanged since only `B` is signed — and it matches, so validation passes: [6](#0-5) .
4. `Registry.process` dispatches the handler with `shop: request.shop == "victim.myshopify.com"` and the attacker-controlled body `B`, even though `B` was never generated for `victim.myshopify.com`: [5](#0-4) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
