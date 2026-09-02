### Title
Webhook shop-domain header is unsigned and unbound to the HMAC-verified body, enabling cross-shop replay confusion - (File: `lib/shopify_api/webhooks/request.rb`)

### Finding Description
The binding the framework needs to hold is: **shop authenticated by the HMAC == shop delivered to the handler**. In practice `Webhooks::Request#shop` reads the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` header directly with no cross-check against the signed payload: [1](#0-0) 

`to_signable_string`, which is what `HmacValidator` actually authenticates, is defined as only the raw body bytes: [2](#0-1) 

`HmacValidator.validate_signature` computes and compares the HMAC exclusively over `to_signable_string` (i.e. the body), never over any header: [3](#0-2) 

`Registry.process` gates handler execution solely on this body-only HMAC check, then forwards `request.shop` (the unsigned header) straight into `WebhookMetadata` given to the app's handler as if it were an authenticated fact: [4](#0-3) 

**Exploit flow:** Shopify apps are typically single-tenant on the signing secret — the same `api_secret_key` (app client secret) is used to sign webhooks for *every* shop that installs the app. An attacker installs their own development shop on the target app, triggers a real event (e.g. `customers/redact`, `orders/create`), and receives a genuinely Shopify-signed webhook whose signature covers only the JSON body. The attacker then replays that exact body to the app's webhook endpoint, substituting the `x-shopify-shop-domain` header with a victim merchant's domain. Because the signature never covered the domain header, `HmacValidator.validate` still returns `true`, and `Registry.process` hands the (attacker's real, HMAC-valid) body to the handler tagged with the victim's shop. There is also no nonce/timestamp/delivery-id tracking anywhere in `Request` or `Registry`, so the same signed body can be replayed indefinitely with different forged domain headers.

Existing guards do not stop this: `HmacValidator.validate` only proves body integrity/authenticity from *some* installation of the app, not which shop it originated from; there is no `ShopValidator.sanitize!`/session lookup binding `request.shop` back to the signature; `JwtPayload`, `Context.setup?`/`private?`, and Sorbet typing are irrelevant to this webhook path — they only cover the OAuth/session-token flow, not `Webhooks::Request`.

### Impact Explanation
An app that trusts `WebhookMetadata#shop` to select which shop's data to mutate (a documented, expected usage pattern demonstrated in this gem's own tests, e.g. `test/webhooks/registry_test.rb`'s `data.shop` assertions) can be made to apply attacker-controlled event data under a victim shop's identity. For the mandatory `customers/redact` / `shop/redact` topics this is most severe: an attacker can force a redact/delete action to be processed under a victim merchant's shop id, i.e. cross-tenant data impact triggered entirely from the attacker's own webhook traffic. This matches the "cross-tenant access" / authentication-bypass class (an unauthenticated value — the shop header — being trusted as if it were authenticated by the signature).

### Likelihood Explanation
Preconditions: the target app must actually rely on the gem's default `Webhooks::Registry`/`Request#shop` without adding its own shop-header/signature cross-binding (the gem provides no such binding, so any app following the documented API is affected). The attacker only needs to install the target app on their own free development shop, capture one legitimately signed webhook, and resend it with a modified header via a normal HTTP client — no possession of `api_secret_key` is required, and the attack is repeatable against arbitrary victim shop domains and arbitrary numbers of retries.

### Recommendation
Bind the shop identity into what is actually authenticated: either (a) include the shop domain in the signable string / compute a per-shop-scoped HMAC, or (b) require the app-provided handler/registry to independently verify that the shop delivered in the header is one the app has an active installation/session for and reject anything else, and (c) add delivery-id/timestamp tracking to prevent replay in general. At minimum, document loudly that `Webhooks::Request#shop` is unauthenticated and must not be trusted for authorization decisions without an out-of-band shop verification step.

### Proof of Concept
```ruby
# test/webhooks/registry_test.rb style addition
def test_shop_header_not_bound_to_hmac_allows_domain_spoof
  real_shop = "attacker-shop.myshopify.com"
  victim_shop = "victim-shop.myshopify.com"
  body = "{}"

  hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
  signed_headers_for_attacker = {
    "x-shopify-topic" => "customers/redact",
    "x-shopify-hmac-sha256" => Base64.encode64(hmac),
    "x-shopify-shop-domain" => real_shop,
  }

  # Attacker replays the SAME signed body, only swapping the domain header
  forged_headers = signed_headers_for_attacker.merge("x-shopify-shop-domain" => victim_shop)

  forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)

  # Signature still validates because to_signable_string == raw_body only
  assert(ShopifyAPI::Utils::HmacValidator.validate(forged_request))
  # But the "authenticated" shop is now attacker-controlled
  assert_equal(victim_shop, forged_request.shop)
  refute_equal(real_shop, forged_request.shop)
end
```
This demonstrates `to_signable_string` (the bytes HMAC actually covers) is identical for both the genuine and forged requests while `#shop` diverges, proving the header is unauthenticated and freely relabelable across shops without invalidating the signature.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
