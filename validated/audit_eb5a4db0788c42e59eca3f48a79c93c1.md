### Title
Webhook `shop` domain is not bound by the HMAC, allowing cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` domain used to route/attribute the webhook is read from a separate, unsigned header. `Registry.process` validates the HMAC and then trusts `request.shop` verbatim when dispatching to the app's handler, so the "shop" identity is never actually covered by the cryptographic check that is supposed to authenticate the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from the `shop-domain` header independently, and is not part of the signed content at all: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `hmac == HMAC(secret, to_signable_string)`, i.e. it only authenticates the body bytes: [3](#0-2) 

`Registry.process` checks the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop_claimed_in_header == shop_that_the_HMAC_actually_authenticates`

but since `to_signable_string` never includes `shop`, this equality is never enforced — the HMAC only proves "this body byte-string was signed with our secret at some point," not "this body belongs to this shop." Because every shop that has installed the app shares the same `api_secret_key`, any tenant that legitimately receives one authentic `(body, hmac)` pair from Shopify holds a value that will pass `HmacValidator.validate` for **any** shop header it chooses to send alongside that same body when POSTing directly to the app's public webhook endpoint.

### Impact Explanation
An attacker who is a legitimate (but unprivileged relative to other merchants) installer of the app can capture a real webhook delivery for their own shop (body + hmac), then replay that exact body/hmac pair to the same public webhook endpoint while substituting an arbitrary `shop-domain` header for a victim shop. `HmacValidator.validate` still succeeds because the shop header plays no role in the signature. `Registry.process` then dispatches to the app's `WebhookHandler` with `WebhookMetadata#shop` set to the victim's domain and `body` taken from the attacker's own webhook payload. Any host application logic that uses `data.shop` to decide which tenant's records to update (e.g. `customers/redact`, `orders/create`, `app/uninstalled` handling) can be made to act on the wrong tenant, i.e., cross-tenant data confusion/corruption originating purely from the gem's failure to bind `shop` into the authenticated payload.

### Likelihood Explanation
Any app developer using this gem for webhook delivery is affected, because the vulnerable binding is entirely inside `Webhooks::Request`/`Registry.process`, which every consumer relies on. The prerequisite — obtaining one authentic `(body, hmac)` pair — is trivially satisfiable by any unprivileged user who installs the app on their own shop, since they will legitimately receive real webhooks for that shop with valid signatures. No secret material, token theft, or privileged access is required beyond ordinary app installation.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signable content used for HMAC verification, or otherwise cryptographically bind the `shop` header to the signed body before it is trusted in `Registry.process`. At minimum, `Registry.process` should reject requests where the shop asserted in the header cannot be tied back to the specific signed payload, rather than trusting it unconditionally once the body-only HMAC passes.

### Proof of Concept
```ruby
# Attacker legitimately installs the app on their own shop "attacker.myshopify.com"
# and receives a real webhook from Shopify:
raw_body = '{"id":123,"note":"attacker-controlled payload"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
# (attacker knows this hmac because it was delivered to their own endpoint)

# Attacker now POSTs directly to the app's public webhook endpoint,
# reusing the same body/hmac but swapping the shop header to a victim shop:
headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => Base64.encode64(hmac),
  "shopify-shop-domain" => "victim-shop.myshopify.com", # forged, unsigned
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true, because to_signable_string only covers raw_body.
# Handler is invoked with WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker's data)
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
