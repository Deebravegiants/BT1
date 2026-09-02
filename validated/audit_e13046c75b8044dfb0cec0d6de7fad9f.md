### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing via signature replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body. The `shop` (tenant) identity that is handed to the app's webhook handler comes from an HTTP header that is never part of the signed material. An attacker who can obtain one *validly signed* webhook body/HMAC pair (e.g., by installing the app on a shop they control) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` / `x-shopify-shop-domain` header, and the gem will accept it as authentic and hand it to the handler tagged with the attacker-chosen shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from a header with no binding to the signature at all: [2](#0-1) 

`Utils::HmacValidator.validate` computes the expected signature purely from `verifiable_query.to_signable_string` (i.e. the body) and compares it to the `hmac` field — `shop` never enters the computation: [3](#0-2) 

`Registry.process` performs exactly that HMAC check and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the equality the HMAC is supposed to enforce is "bytes verified == bytes the shop identity is derived from," but `shop` is not part of "bytes verified," any request whose *body* matches a previously-signed body will pass validation regardless of which shop header accompanies it. An unprivileged attacker who legitimately installs the app on their own store receives real Shopify webhooks with real HMACs over the body. They can capture one such `(body, hmac)` pair and resend it to the app's public webhook endpoint with the `shop` header rewritten to any victim shop domain. `Registry.process` will validate the HMAC successfully and dispatch the payload to the handler as if it originated from the victim shop, achieving cross-tenant data injection/spoofing without ever needing the app's `client_secret`, `api_secret_key`, or any victim credential.

### Impact Explanation
This breaks the tenant binding that host applications rely on: `HmacValidator.validate(request) == true` is treated as proof that "this body legitimately belongs to `request.shop`," when in fact it only proves "this body was signed by *some* valid Shopify webhook for *some* shop using this app's secret." An app that keys any downstream logic (order/customer records, inventory sync, billing side effects, per-shop feature flags, etc.) off `WebhookMetadata#shop` can be made to apply attacker-controlled webhook content to a shop the attacker does not own — a cross-tenant integrity/confidentiality issue.

### Likelihood Explanation
Exploitability only requires that the attacker install the app on their own shop (or otherwise obtain one signed webhook body for a topic that produces attacker-influenceable body content, such as a topic where the merchant controls some field value, e.g. a metafield or order note) and then send a normal HTTP POST to the app's public webhook endpoint with a modified shop header. No privileged credentials, secrets, or victim interaction are required, so likelihood is high for any app whose webhook handling trusts `shop` from `WebhookMetadata` for tenant-scoped effects.

### Recommendation
Bind the shop identity into the authenticated material before trusting it: either include the shop domain (and topic) in the signable string used by `Utils::HmacValidator.validate`, or independently verify that `request.shop` corresponds to a shop with an existing, valid session/installation record before invoking the handler. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and must be cross-checked by the host application against known installed shops before being trusted for tenant-scoped operations.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) whose body content the attacker can influence (order note, custom field, etc.).
2. Capture the raw body `B` and the `shopify-hmac-sha256` header `H` that Shopify sent for that legitimate webhook, per `ShopifyAPI::Webhooks::Request#hmac` / `#to_signable_string`: [5](#0-4) 
3. Send a new POST to the app's webhook endpoint with body `B`, header `shopify-hmac-sha256: H` (unchanged), and `shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` (see `hmac_validator.rb` lines 26-31), and `Registry.process` dispatches `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed(B), ...)` to the handler, which now processes attacker-supplied content as if it came from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
