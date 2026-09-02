### Title
Webhook shop-domain header is trusted without being covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds, but the HMAC only ever covers the raw request body — never the `shop-domain` header that is subsequently handed to the app's handler as the tenant identifier. An attacker who controls any shop that has the target app installed can capture a validly-signed webhook body for their own shop and replay it against the app's webhook endpoint with the `shop-domain` header swapped to a victim shop, producing a request that passes HMAC validation while impersonating the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from an HTTP header that is never part of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes/compares the signature only against `verifiable_query.to_signable_string` (i.e. the body), never against the shop header: [3](#0-2) 

`Registry.process` gates entirely on that same HMAC check and then forwards `request.shop` unchanged, as the tenant identity, to the app's handler: [4](#0-3) 

The identity binding the library implicitly claims to provide is:
`hmac_valid(raw_body) == true  ⇒  shop header is authentic`

But the actual binding enforced is only:
`hmac_valid(raw_body) == true  ⇒  raw_body is authentic (signed by Shopify with this app's shared secret)`

Because the app's `api_secret_key` is shared across every shop that installs the app, any shop owner (an unprivileged internet user who simply installs the app on their own store) can generate an arbitrary, validly-HMAC-signed webhook body for their own tenant, capture it, and then replay it to the app's webhook controller with only the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` still succeeds because the raw body used to compute/verify the signature is untouched — only the unauthenticated header changed. `WebhookMetadata.shop` in the handler payload is set from that same untouched-by-signature header: [5](#0-4) 

This is confirmed by the test suite, which builds the HMAC purely from the body and independently sets the shop header: [6](#0-5) 

### Impact Explanation
Any app built on this gem that uses the `shop` value delivered in `WebhookMetadata` to key tenant-scoped actions (loading the shop's session/access token, updating per-shop records, processing `app/uninstalled`, `shop/redact`, order/customer data changes, etc. — the exact pattern shown in the gem's own webhook usage docs) can be made to perform those actions against a shop the attacker does not control, using only a webhook payload the attacker legitimately received for their own shop. This is a cross-tenant access primitive: an unprivileged installer of the app can spoof webhook events "from" any other shop using the app, without ever needing the app's `client_secret`, an access token, or any privileged credential — they only need Shopify to sign a webhook for their own (attacker-owned) shop and the ability to POST an HTTP request to the app's public webhook endpoint.

### Likelihood Explanation
Likelihood is high for any deployment that follows the gem's documented webhook pattern: `Registry.process` is presented as the single authentication check ("This will verify the request did indeed come from Shopify"), and nothing in the gem or its docs indicates that the `shop` field on `WebhookMetadata` requires independent authentication against a known/installed shop. An attacker needs only their own free Shopify dev/trial store with the target app installed, network access to trigger a webhook-firing action, and the ability to replay one crafted HTTP request with a modified header — all achievable by an unprivileged internet user with no special access.

### Recommendation
Include the tenant-identifying header(s) (`shop-domain`, and ideally `topic`/`webhook-id`/`api-version`) in the HMAC-signed material that `Utils::HmacValidator` verifies, or otherwise cryptographically bind them to the body before trusting them. At minimum, `Registry.process` should cross-check the header-derived `shop` against a shop that is known to have a valid installation/session before invoking the handler with it, rather than passing the raw, unauthenticated header value straight through to `WebhookMetadata`.

### Proof of Concept
Using the existing test harness pattern (`test/webhooks/registry_test.rb`) as a model:

```ruby
# Attacker computes this legitimately for THEIR OWN shop ("attacker-shop.myshopify.com"),
# since Shopify will sign any webhook body with the app's shared api_secret_key
# regardless of which installed shop triggered it.
body = "{}"
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)

# Attacker now replays the exact same body/signature but swaps only the shop header
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # <-- not covered by HMAC
}

forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)

# Passes: HmacValidator only checks `body`, never the shop header
ShopifyAPI::Webhooks::Registry.process(forged_request)
# => handler.handle(data: WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", ...))
```

`Registry.process` accepts this request and invokes the registered handler with `shop == "victim-shop.myshopify.com"`, even though the request never originated from that shop, because `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb#L12-31`) validates only the untouched `body`, not the attacker-modified `shop-domain` header.

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

**File:** test/webhooks/registry_test.rb (L16-33)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
        @session = ShopifyAPI::Auth::Session.new(shop: ShopifyAPI::Context.host_name, access_token: "access_token")
        @url = "#{ShopifyAPI::Context.host}/admin/api/#{ShopifyAPI::Context.api_version}/graphql.json"
      end
```
