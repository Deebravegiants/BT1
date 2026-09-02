### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant spoofing / cross-tenant data injection - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts a separate, unsigned header (`shopify-shop-domain` / `x-shopify-shop-domain`) as the tenant identifier passed to the app's handler. Because the shop domain is never part of the signed content, the binding "HMAC-authenticated request == HMAC-authenticated shop" does not hold: an attacker who possesses one genuinely-signed webhook body (which they can obtain simply by being a normal installer of the app and receiving their own webhooks) can replay that exact body to the app's webhook endpoint while substituting a victim shop's domain in the header, and the signature check still passes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read from a header that is completely independent of that signed string: [2](#0-1) 

`Utils::HmacValidator.validate` computes/compares the HMAC only over `verifiable_query.to_signable_string` (i.e., the raw body) using the app-wide `Context.api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC and, on success, immediately forwards the unsigned `request.shop` value to the application's webhook handler as the trusted tenant identifier: [4](#0-3) 

The critical detail is that `api_secret_key` is the **app's** single secret, shared across every merchant/shop that has installed the app — it is not shop-specific. Consequently, any low-privilege merchant that has installed the app receives real, validly-HMAC'd webhook deliveries for their own shop. Because the shop domain is excluded from the signed bytes, that same attacker can capture one such body+HMAC pair and replay it to the app's public webhook endpoint with the `shopify-shop-domain` header changed to point at a different, victim shop that also uses the same app. The signature verification (`Utils::HmacValidator.validate`) still succeeds because it only checks the (unmodified) body, and `Registry.process` never cross-checks that the header-supplied shop is consistent with anything cryptographically verified.

This breaks the intended identity binding:
`HMAC-verified(body) == HMAC-verified(shop)`
which the code implicitly assumes to be true (the equality actually enforced is `HMAC-verified(body)`, while `shop` is merely `parsed-but-unverified(header)`).

### Impact Explanation
Any app that keys tenant-scoped logic off `WebhookMetadata#shop` (e.g., looking up the merchant's stored session/access token to process the event, writing to a per-shop database record, or triggering shop-scoped side effects) can be made to attribute attacker-controlled webhook content to an arbitrary victim shop that also uses the app. This is a cross-tenant data/identity confusion vulnerability reachable by any unprivileged merchant that has simply installed the app (no `api_secret_key`, access token, or other privileged credential is required) — it matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app built on this gem that follows the documented webhook pattern of trusting `WebhookMetadata#shop` for tenant-scoped operations: any of the app's own merchants can capture one of their own legitimate webhook deliveries (trivial — they own the shop and can observe traffic to their own endpoint or via a proxy) and replay it with a modified `shop-domain` header, requiring no access to the app's `client_secret` or any other party's credentials.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-signed material, or independently verify that the `shopify-shop-domain` header corresponds to an actual installed/known shop associated with the delivered webhook (e.g., cross-check against Shopify's provided `X-Shopify-Shop-Domain` only after confirming per-shop context, or require the consuming application to validate the shop against its own session store before trusting it). At minimum, document prominently that `WebhookMetadata#shop` is **not** cryptographically bound to the HMAC and must not be used as a sole tenant-authentication signal without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged installation — no special access needed).
2. Shopify sends the attacker a legitimate webhook, e.g. `orders/create`, to the app's webhook endpoint with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of raw body using app's api_secret_key>`
   - body: `{"id": 1, ...attacker-controlled order data...}`
3. Attacker replays this exact request to the same endpoint, changing only the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - keeping the same body and the same (still-valid) `x-shopify-hmac-sha256`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body successfully; `Utils::HmacValidator.validate` recomputes HMAC over the (unchanged) raw body and it matches — validation succeeds per [5](#0-4) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled body content, exactly as constructed in [6](#0-5) , despite none of that data actually originating from Shopify on behalf of the victim shop.

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
