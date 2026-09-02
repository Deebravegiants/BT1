### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) for an incoming webhook from the `X-Shopify-Shop-Domain` header, but the HMAC signature that authenticates the webhook only covers the raw request body. `Registry.process` validates the HMAC and then hands `request.shop` straight to the app's handler as the authenticated tenant identity, so the shop-domain binding is never actually verified.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header, a value that is not part of that signable string: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)` (which hashes `to_signable_string`, i.e. the body only) and then constructs `WebhookMetadata` using `request.shop` as the authenticated tenant, passing it directly to the registered handler: [3](#0-2) 

`HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string`: [4](#0-3) 

This is the same bug class as the report: a field that is acted upon (the shop/tenant identity, analogous to the token amount in the swap) is not covered by the integrity check (HMAC, analogous to the fee-enforcing `_swap()` path) that a parallel path (the `deposit`/`withdraw` pair, analogous to simply relabeling `shop-domain` while keeping the signed body unchanged) is able to bypass. Concretely: `HMAC == HMAC(raw_body)` says nothing about `shop-domain == shop-domain`, so an attacker who possesses one valid `(raw_body, hmac)` pair for their own store can replay it with a different `shop-domain` header and it will still pass `HmacValidator.validate`.

By contrast, the OAuth callback binds `shop` into the signed string explicitly: [5](#0-4) 

showing that the library is capable of, and elsewhere does, bind the tenant identifier into the HMAC — but the webhook path does not do the same.

### Impact Explanation
Any application built on this gem that stores or acts on `data.shop` from `WebhookMetadata` (e.g., to key a database record, trigger `shop/redact`, `customers/redact`, `app/uninstalled` cleanup, or attribute order/customer data to a specific merchant) can be fed a request whose body was legitimately signed for one shop but whose `shop-domain` header claims to be a different shop. Since a merchant installing the app fully controls their own store and can trigger arbitrary legitimate webhooks with valid HMACs (e.g. by placing test orders, or via mandatory topics), they can capture a `(body, hmac)` pair and replay it to the app's public webhook endpoint with an arbitrary victim `shop-domain` header. This is a cross-tenant data-integrity/authentication issue: the app believes fabricated or misattributed data originated from a shop it did not, which qualifies as Critical (cross-tenant access) under the given impact ontology.

### Likelihood Explanation
The webhook endpoint is a public HTTP endpoint (webhooks are delivered over the open internet to the app's registered callback URL), and the header the attacker needs to control (`X-Shopify-Shop-Domain`) is a plain HTTP header, trivially forged by anyone who can send an HTTP request to that endpoint. The only prerequisite is possession of one valid `(raw_body, hmac)` pair, which any merchant with the app installed on their own store can obtain legitimately through normal use (e.g., triggering `orders/create`), requiring no privileged credentials, no `api_secret_key`, and no access token.

### Recommendation
Bind the shop domain (and ideally topic/webhook-id) into the value that is HMAC-verified, or independently verify that `request.shop` matches an expected/registered shop for that installation before trusting it in `WebhookMetadata`. At minimum, document and enforce that host applications must not treat `request.shop`/`data.shop` as authenticated unless it is cross-checked against a known session/shop record, since the HMAC in this gem's `Request#to_signable_string` does not cover it.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com"
# and triggers any webhook (e.g. orders/create), capturing:
raw_body = '{"id":123,"note":"legit order"}'
valid_hmac_for_body = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)
hmac_b64 = Base64.encode64(valid_hmac_for_body)

# Attacker replays the identical body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds because it only hashes raw_body.
# The registered handler receives WebhookMetadata with shop == "victim-shop.myshopify.com",
# even though the payload/HMAC were only ever generated for "attacker.myshopify.com".
``` [3](#0-2) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
