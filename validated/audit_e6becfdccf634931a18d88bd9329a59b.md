## Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header not covered by HMAC — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, while the `shop` value that is handed to the host application's handler is taken from an HTTP header that is never included in the signed material. This breaks the intended identity binding `HMAC-authenticated bytes == tenant identity acted upon`, allowing an attacker who can obtain one validly-signed webhook (e.g., by installing the app on their own store) to relay it to the app's webhook endpoint with a forged `shop-domain` header pointing at a victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is a plain, unauthenticated header, not part of the signed string: [2](#0-1) 

`HmacValidator.validate` computes and compares the signature only against `verifiable_query.to_signable_string` (the body), never against the shop header: [3](#0-2) 

`Registry.process` uses this HMAC check as its sole authentication gate, and then dispatches the handler using `request.shop` taken straight from the unauthenticated header: [4](#0-3) 

Because the webhook secret (`Context.api_secret_key`, the app's `client_secret`) is the same for every shop that installs the app, an unprivileged internet user can:
1. Install the target Shopify app on a shop they control.
2. Trigger any webhook to obtain a body + valid HMAC pair signed with the app's shared secret.
3. Replay that exact `raw_body`/HMAC pair directly to the app's webhook endpoint, but with the `x-shopify-shop-domain` header rewritten to the victim's shop domain.

`Utils::HmacValidator.validate` will report the signature as valid (it only checks the body bytes), and `WebhookMetadata.shop` will contain the attacker-chosen victim domain: [5](#0-4) 

The equality the code should enforce but does not is: `HMAC-verified identity (shop) == identity passed to the handler`. Instead, only `HMAC-verified bytes (body) == body`, while `shop` is trusted unauthenticated.

### Impact Explanation
Host applications built on this gem (per the documented pattern, e.g. `shopify_app`) key session storage, access-token lookup, and compliance actions (GDPR redact, `app/uninstalled`, etc.) by `WebhookMetadata#shop`. An attacker can forge a webhook payload that appears to originate from a shop they do not control (e.g. spoof `app/uninstalled` or `shop/redact` for a victim shop), causing cross-tenant state corruption such as deletion of the victim's stored session/access token, or processing of attacker-controlled data under the victim tenant's identity. This falls under "cross-tenant access", the gem's own Critical severity category.

### Likelihood Explanation
The prerequisite is trivial for any unprivileged internet user: installing a public Shopify app on a free development store is unauthenticated and self-service, giving the attacker a legitimately signed body/HMAC pair. Constructing a raw HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header requires no special access, since the check in `Registry.process` never binds the header to the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signable string used for HMAC verification, or independently verify that `request.shop` corresponds to a shop with an active installation/session known to the host app before dispatching to the handler. At minimum, `Utils::HmacValidator` should be extended so that `VerifiableQuery#to_signable_string` for webhooks incorporates the shop domain header, so a signature computed for one shop cannot be replayed with a different shop header.

### Proof of Concept
```ruby
# Attacker installs the target app on shop "attacker.myshopify.com" and
# receives a legitimate webhook, e.g. for "orders/create":
#   raw_body = '{"id":1}'
#   valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"),
#                                      shared_client_secret, raw_body)

# Attacker replays the exact same body/HMAC to the app's public webhook
# endpoint, but swaps the shop-domain header to the victim's shop:
forged_headers = {
  "x-shopify-topic"        => "app/uninstalled",
  "x-shopify-hmac-sha256"  => Base64.encode64(valid_hmac), # unchanged, body unchanged
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only checks raw_body),
#    handler.handle is invoked with shop: "victim-shop.myshopify.com",
#    even though the payload never originated from Shopify for that shop.
``` [6](#0-5) [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
