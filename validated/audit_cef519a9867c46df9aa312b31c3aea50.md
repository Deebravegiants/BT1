### Title
Webhook shop identity spoofing via unsigned `X-Shopify-Shop-Domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body: [1](#0-0) [2](#0-1) 

The signable string used for that HMAC check is defined as just the raw body bytes: [3](#0-2) 

However, the `shop` (tenant) identity that the handler receives and treats as authoritative comes from an HTTP header that is never part of the signed bytes: [4](#0-3) 

`Registry.process` passes this unauthenticated header value straight into the `WebhookMetadata` handed to the app's handler: [5](#0-4) 

This reproduces the exact bug class from the external report: the field that is *acted on* (`shop`, which downstream app code uses as the tenant key, analogous to `to_handler`) is not the field that is *covered by the cryptographic check* (`raw_body`/HMAC, analogous to the settlement contract using `address(this)` instead of the correct handler field). The equality that should hold is:

`bytes_covered_by_HMAC == bytes_that_determine_tenant_identity`

but in this gem it is actually:

`bytes_covered_by_HMAC (raw_body) != tenant_identity_source (shop-domain header)`

### Impact Explanation
Because the app's shared `api_secret_key` is common to all shops that install the app, any unprivileged merchant can install the app on their own store and receive a legitimately Shopify-signed webhook (valid `raw_body` + valid `hmac-sha256`). That attacker can replay the exact same body/HMAC pair to the app's webhook endpoint while forging the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header to a victim shop's domain. `HmacValidator.validate` will accept it (the HMAC only covers `raw_body`, which is unchanged), and `Registry.process` will invoke the registered handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain. Any host application that uses `data.shop` to select the tenant/session, write data, or trigger the mandatory GDPR flows (`shop/redact`, `customers/redact`, `customers/data_request`) will process the payload under the wrong tenant, causing cross-tenant data confusion/leakage or forged customer-data-request/redaction requests against a shop the attacker doesn't control — an authentication/tenant-binding bypass, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app relying on this gem's built-in webhook `Registry`/`Request` without additional out-of-band shop verification: the only prerequisite is that the attacker can install the target app on a store they control (a normal, unprivileged action) to obtain one valid signed body/HMAC pair, then replay it with a forged shop-domain header — no access to `api_secret_key`, tokens, or victim credentials is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`) values into the HMAC-covered signable content, or otherwise cryptographically verify that the shop domain in the header actually corresponds to a shop session/state your app expects (e.g., cross-check against `shop` embedded in the parsed payload rather than trusting the header verbatim). At minimum, document and enforce that `WebhookMetadata#shop` must never be treated as more trustworthy than an unauthenticated header, or move to comparing it against separately stored/verified shop state before acting on it.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, triggering Shopify to send a legitimate webhook: `raw_body = B`, header `X-Shopify-Hmac-Sha256 = HMAC(secret, B)`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays the identical `raw_body = B` and the identical valid HMAC header to the same webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, request.to_signable_string)` i.e. `HMAC(secret, B)` — this still matches, per [3](#0-2)  and [6](#0-5) .
4. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` using the forged header value `victim-shop.myshopify.com`, per [5](#0-4) , and invokes the app's handler as if the event legitimately originated from the victim shop.

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
