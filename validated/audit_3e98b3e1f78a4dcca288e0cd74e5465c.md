### Title
Webhook shop-domain (and topic) is trusted without being covered by the HMAC signature, enabling cross-tenant webhook confusion - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by validating an HMAC that is computed **only over the raw request body**, yet the `shop` (and `topic`) values that are subsequently trusted and handed to the app's webhook handler are read from HTTP headers that are **not included in the signed bytes**. This breaks the intended binding `HMAC-verified bytes == data the app acts on`, allowing a party who has legitimately obtained one valid `(body, hmac)` pair (e.g., by owning/installing the app on their own shop) to relabel that same signed payload as coming from a different shop by simply changing the `X-Shopify-Shop-Domain` header.

### Finding Description
The signable string for a webhook request is defined as just the raw body: [1](#0-0) 

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

`Registry.process` validates only this HMAC and then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version`, all of which come from headers outside the signed data: [2](#0-1) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

and `shop` is read straight from an attacker-controllable header: [3](#0-2) 

```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
```

The identity binding that should hold is:
`shop-domain header value == shop that was authenticated by the HMAC`

but the actual bytes verified by `HmacValidator.validate` are `HMAC(secret, raw_body)`, which says nothing about which shop the payload belongs to. Therefore the equality above does not hold — the gem verifies the body's integrity/authenticity but not its association with a particular shop.

This mirrors the report's bug class ("a field acted on but not covered by the HMAC"): in the Solidity report, `contribution` was checked against limits that didn't account for values not covered by the same accounting; here, `shop` is acted upon by the handler (used for tenant routing, e.g. `WebhookHandler#handle` typically looks up per-shop credentials/session using `data.shop`) despite not being part of the cryptographically bound data.

### Impact Explanation
Any actor who can obtain one genuinely Shopify-signed `(raw_body, hmac)` pair for the target app — trivially achievable by installing the app on their own store and capturing/replaying one of their own webhooks — can submit that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `Utils::HmacValidator.validate` will still succeed (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop. Depending on how the host application uses `data.shop` (commonly to look up the shop's session/access token or to scope database writes), this enables cross-tenant data confusion/injection — a webhook payload from the attacker's own shop can be processed under a victim shop's identity. This falls under the Critical "cross-tenant access" category.

### Likelihood Explanation
Any internet-reachable attacker who can install the target app on a shop they control (a normal, permission-free action for public/embedded Shopify apps) can obtain valid `(body, hmac)` pairs at will and forge the shop-domain header on replay, since no additional secret or privileged credential is required to alter unsigned headers. The only precondition is that the receiving application uses `data.shop` for tenant-sensitive logic, which is the documented and expected usage pattern shown in this gem's own webhook docs.

### Recommendation
Include the shop domain (and ideally topic/webhook_id/api_version) in the HMAC-signed material, or independently bind them — e.g., require the caller to pass the expected shop for the endpoint and compare it against `request.shop`, or verify that the HMAC header itself is scoped per-shop via a signed URL/path segment that is included in `to_signable_string`. At minimum, document prominently that `shop`, `topic`, and other headers are unauthenticated and must not be trusted for tenant routing without additional verification (e.g., cross-checking against the shop associated with the webhook subscription that was registered).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the legitimate request Shopify sends, including body `raw_body` and header `X-Shopify-Hmac-Sha256`.
2. Attacker replays this exact `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. In the gem:
```ruby
request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac_header,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
})
ShopifyAPI::Webhooks::Registry.process(request)
```
4. `Utils::HmacValidator.validate(request)` succeeds because it only recomputes HMAC over `raw_body`, matching the captured signature — as shown by `to_signable_string` in [1](#0-0)  and the validation logic in [4](#0-3) .
5. `WebhookMetadata.shop` is set to `"victim-shop.myshopify.com"` and passed to the app's handler, as in [5](#0-4) , despite that value never having been authenticated by Shopify's HMAC for this payload.

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
