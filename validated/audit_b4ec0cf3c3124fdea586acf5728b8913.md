### Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the handler using the `shop` value taken from an HTTP header that is **not part of the signed material**. An attacker who possesses one genuine, validly-signed webhook delivery (e.g. from their own store, where they are the merchant/tenant who legitimately receives webhooks for an installed app) can replay that exact `body` + `hmac` pair while substituting the `X-Shopify-Shop-Domain` header for a different, victim shop. The HMAC still validates (it only covers the body), but the handler is invoked believing the data belongs to the victim tenant.

### Finding Description
The bug class from the report is: a field the code *acts on* is not covered by the cryptographic check that is supposed to bind it to an identity — analogous to Eig's withdrawal credential prefix not being validated.

In `lib/shopify_api/webhooks/request.rb` lines 21–23, the `shop` property is extracted directly from the HTTP header:

```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
```

In `lib/shopify_api/webhooks/registry.rb` line 190, the webhook is validated:

```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

The `HmacValidator.validate` method (in `lib/shopify_api/utils/hmac_validator.rb` lines 13–21) calls `validate_signature`, which computes the HMAC over `verifiable_query.to_signable_string`. For webhooks, this is defined in `lib/shopify_api/webhooks/request.rb` line 37:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

The HMAC is computed **only over the raw body**, not over the `shop` header. Then, in `lib/shopify_api/webhooks/registry.rb` lines 198–199, the handler is invoked with the shop from the untrusted header:

```ruby
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

The `shop` field is acted upon (passed to the handler, used to route the webhook to the correct tenant's logic) but is not bound by the HMAC signature.

### Impact Explanation
**Critical** — Cross-tenant access. An attacker who has legitimate webhook delivery access to their own Shopify store (where they have installed the app) can:

1. Capture a valid webhook delivery (e.g., `orders/create`) with a valid HMAC signature.
2. Modify only the `X-Shopify-Shop-Domain` header to point to a victim merchant's shop.
3. Replay the request to the app's webhook endpoint.
4. The HMAC validation passes (it only covers the body, which is unchanged).
5. The handler processes the webhook as if it came from the victim shop, allowing the attacker to:
   - Trigger business logic tied to the victim's orders, customers, or other resources.
   - Potentially manipulate the victim's data if the handler performs mutations.
   - Exfiltrate or corrupt the victim's webhook data.

This breaks the authentication boundary between tenants. The app cannot distinguish between a webhook legitimately sent by Shopify for the victim shop and a replayed webhook from the attacker's shop with a forged shop header.

### Likelihood Explanation
**High** — The vulnerability is trivial to exploit:
- No special knowledge of cryptography is required; the attacker simply replays a captured request with a modified header.
- Any app using `ShopifyAPI::Webhooks::Registry.process` is vulnerable.
- The attacker needs only to be a legitimate merchant with the app installed (a low bar).
- The attack is undetectable without additional logging or shop-specific validation.

### Recommendation
Bind the `shop` domain to the HMAC signature. Modify `lib/shopify_api/webhooks/request.rb` to include the shop domain in the signable string:

```ruby
sig { override.returns(String) }
def to_signable_string
  # Include shop domain in the signed material to bind it to the HMAC
  params = {
    shop: shop,
  }
  URI.encode_www_form(params) + @raw_body
end
```

Alternatively, validate that the shop domain is a trusted Shopify domain using `ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain` before processing, though this does not prevent cross-tenant replay.

### Proof of Concept

```ruby
# Attacker's shop: attacker.myshopify.com
# Victim's shop: victim.myshopify.com

# Step 1: Attacker captures a valid webhook from their own store
original_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(
    OpenSSL::HMAC.digest(
      OpenSSL::Digest.new("sha256"),
      ShopifyAPI::Context.api_secret_key,
      '{"order":{"id":123}}'
    )
  ),
  "x-shopify-shop-domain" => "attacker.myshopify.com",
}

# Step 2: Attacker replays the same body and HMAC but changes the shop header
malicious_headers = original_headers.dup
malicious_headers["x-shopify-shop-domain"] = "victim.myshopify.com"

# Step 3: The webhook is processed as if it came from victim.myshopify.com
webhook_request = ShopifyAPI::Webhooks::Request.new(
  raw_body: '{"order":{"id":123}}',
  headers: malicious_headers
)

# This passes validation because the HMAC only covers the body
ShopifyAPI::Webhooks::Registry.process(webhook_request)
# Handler is invoked with shop: "victim.myshopify.com"
# Attacker has successfully spoofed a webhook for the victim tenant
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L21-23)
```ruby
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
