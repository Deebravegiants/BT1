### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `Registry.process` is computed only over the raw request body. This breaks the identity binding `shop (HMAC-verified) == shop (acted upon)`: the HMAC proves the body was produced with the app's `client_secret`, but it says nothing about which shop the body belongs to, since the shop domain is never part of the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` value is taken straight from a header and is never included in that signable string: [2](#0-1) 

`Registry.process` validates only this body-based HMAC and then immediately hands `request.shop` to the app's handler as trusted identity data, with no additional check that binds the shop to the signature: [3](#0-2) 

By contrast, the OAuth callback path (`Auth::Oauth::AuthQuery`) does bind `shop` into the signable string that is HMAC-verified, so the two flows are inconsistent: [4](#0-3) 

Because `Utils::HmacValidator.validate` uses `Context.api_secret_key`, which is the same secret for every shop that has the app installed, any actor who can obtain one validly-signed webhook body (e.g., by installing the app on their own shop and receiving a real webhook) can compute/replay a valid HMAC for that body. They can then freely change the `shopify-shop-domain` header to any victim shop domain, since that header is not covered by the signature. The `Registry.process` method will accept the request as authentic and dispatch it to the handler labeled with the attacker-chosen shop: [5](#0-4) 

### Impact Explanation
This qualifies as Critical/cross-tenant access: an attacker-controlled shop identifier is delivered to the host application as if it were verified data from Shopify. Any host application that trusts `WebhookMetadata#shop` (or `Request#shop`) to select which merchant's data/record to update, without independently re-validating the shop against another authenticated source, can be tricked into performing an action against another tenant's data using a payload the attacker fully controls the meaning of (topic, body) combined with a spoofed shop identity — i.e., a cross-tenant write/read triggered by an unprivileged internet user who only needs one legitimate webhook signature they can generate for themselves.

### Likelihood Explanation
Likelihood is high for apps that rely on the gem's `Request`/`WebhookMetadata` objects without extra shop verification, since: (1) obtaining a validly HMAC-signed body only requires installing the app on any shop (a normal, unprivileged action available to any internet user who can install a public app, or triggering any webhook topic on that shop), and (2) the `shop-domain` header can be freely rewritten by the client sending the HTTP request to the app's webhook endpoint, since nothing in this gem cryptographically ties it to the signature.

### Recommendation
Include the shop domain (and other identity-relevant fields, e.g., topic, api-version, webhook-id) in the material that is bound to the HMAC check, or, at minimum, clearly document that `Request#shop`/`WebhookMetadata#shop` is unauthenticated and must be independently confirmed (e.g., by only trusting HTTPS-terminated header values Shopify sets and cross-checking topic-appropriate shop ownership) before being used for tenant-sensitive lookups. Practically, since Shopify's real webhook protocol does not sign the shop-domain header, the fix belongs in this gem's documentation/API: expose the un-trusted nature of `shop` explicitly (e.g., rename/annotate it, or provide a combined verified struct) so integrators do not conflate "HMAC valid" with "shop identity verified."

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and
# receives (or triggers) any real webhook, e.g. an "orders/create" webhook,
# capturing the raw body and its valid X-Shopify-Hmac-Sha256 header value.
raw_body = captured_body           # exact bytes from the genuine webhook
valid_hmac_header = captured_hmac  # base64 HMAC-SHA256, valid because it only signs raw_body

# Attacker crafts a new HTTP request to the app's webhook endpoint using the
# same body/hmac, but overwrites the shop-domain header to target a victim shop.
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_header,   # still valid: body unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # spoofed, unsigned
  "x-shopify-webhook-id" => "attacker-chosen-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC check passes (Utils::HmacValidator.validate only checks raw_body),
#    handler.handle is invoked with WebhookMetadata.shop == "victim-shop.myshopify.com"
#    even though the request was never issued by Shopify for that shop.
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
