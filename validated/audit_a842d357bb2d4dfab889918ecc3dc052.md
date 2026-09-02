Investigating the webhook signature verification in `lib/shopify_api/webhooks/request.rb` confirmed a concrete identity-binding gap: the shop attribution header is not covered by the webhook HMAC.### Title
Webhook shop-domain attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by HMAC-signing only the raw request body, while the `shop` (and `topic`/`webhook_id`) values used to attribute the event to a tenant are taken from unauthenticated HTTP headers. This breaks the identity binding: `hmac(raw_body) == valid` should imply `shop == the shop that produced this body`, but the gem never binds `shop` into the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request` defines:
```ruby
# lib/shopify_api/webhooks/request.rb
def to_signable_string
  @raw_body
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [1](#0-0) 

`Utils::HmacValidator.validate` only checks that the supplied `hmac` matches `HMAC(secret, to_signable_string)`, i.e. `HMAC(secret, raw_body)`: [2](#0-1) 

`Webhooks::Registry.process` then trusts `request.shop` unconditionally to build the event handed to the app's handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

The identity binding that is broken as an equality:
- Expected: `valid_hmac(raw_body, secret) == true` implies `shop_header == shop_that_this_body_and_signature_were_issued_for`.
- Actual: `valid_hmac` only certifies `raw_body`; `shop_header` is disjoint, unauthenticated header data that is never part of `to_signable_string`.

Because the webhook signing secret (`Context.api_secret_key`) is the app's single client secret shared across *every* installed shop, any shop that has legitimately installed the app receives real webhook deliveries `(body, hmac)` pairs that are valid under this same secret. Since `shop` is not part of the signed bytes, an unprivileged holder of any one legitimately-received `(body, hmac)` pair (e.g., their own store's webhook delivery, which any merchant can trivially capture by pointing a webhook endpoint at a server they control, or by replaying/observing a webhook their own store received) can resend that exact `(body, hmac)` pair to the app's webhook endpoint while changing only the `X-Shopify-Shop-Domain` header to a victim shop's domain. `HmacValidator.validate` still returns `true`, and the app-provided handler receives `WebhookMetadata` claiming the event is for the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding bypass: an attacker who is a legitimate (but malicious) installer of the app can forge webhook events "from" a different, victim shop while passing the gem's own signature check. Any app logic that trusts `WebhookMetadata#shop` to select which shop's stored session/access token to act on, or which tenant's data to mutate based on the event body, can be tricked into acting on/for the wrong tenant using data supplied by the attacker's own shop — a cross-tenant access condition, which the rules classify as Critical.

### Likelihood Explanation
Any shop that installs the app already receives legitimate webhook deliveries signed with the shared client secret, so an attacker doesn't need to break cryptography — they merely need one raw `(body, hmac)` pair, which is straightforward to obtain from their own store's webhook traffic (e.g., by configuring the delivery URL to a host they control, or capturing outbound requests). Replaying it with a modified `shop-domain` header is trivial and requires no credentials beyond having installed the app once.

### Recommendation
Bind the shop identity into the verified bytes: e.g., include `shopify-shop-domain` (and ideally `topic`) in `to_signable_string`, or require the caller to independently confirm that `shop` matches a shop for which the app holds an active, previously-established session/installation before trusting the webhook payload. At minimum, cross-check `request.shop` against a known/allow-listed shop registered by the app for that specific webhook subscription rather than trusting the header verbatim.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and configures (or observes) a real webhook delivery, capturing the exact `raw_body` and the `X-Shopify-Hmac-Sha256` header Shopify computed for it using the app's shared secret.
2. Attacker sends a POST to the app's webhook endpoint with:
   - `X-Shopify-Topic: orders/create` (unchanged)
   - `X-Shopify-Hmac-Sha256: <the captured, still-valid signature>` (unchanged)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (modified)
   - Body: the captured `raw_body` (unchanged)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unmodified) body against the (unmodified) signature: [4](#0-3) 
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, even though the event body and signature originated from the attacker's own store, demonstrating the cross-tenant spoof. [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
```ruby
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
