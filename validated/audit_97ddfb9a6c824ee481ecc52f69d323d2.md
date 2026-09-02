This confirms the core structure needed for the finding.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw HTTP body when computing the HMAC used to authenticate an incoming webhook, but the `shop` (tenant identity) is taken from an unauthenticated header. `ShopifyAPI::Webhooks::Registry.process` accepts any request whose body-HMAC is valid and then dispatches the handler with the caller-supplied `shop` value, breaking the binding `HMAC(body) == HMAC(body)` from `shop-domain header == shop that produced the body`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements the `VerifiableQuery` interface. Its `to_signable_string` method returns only the raw request body: [1](#0-0) 

The `shop` accessor, however, is read straight from an HTTP header that is never included in the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the signature purely against `to_signable_string`, i.e. the body, using `Context.api_secret_key`: [3](#0-2) 

`Webhooks::Registry.process` only checks this body-HMAC and then trusts `request.shop` as the tenant identity handed to the app's handler: [4](#0-3) 

Because `shop` is not part of the signed payload, the equality the app relies on — "the shop that produced this HMAC-signed body" == "the shop named in the `shop-domain` header" — is never enforced. Any party that can obtain one valid `(body, hmac)` pair signed with the app's secret (for example, an attacker who has installed the app on their own store and triggers a webhook whose body contains attacker-influenced field values, such as an order note, product title, or customer attribute) can replay that exact body and HMAC to the app's webhook endpoint while substituting a different value in `X-Shopify-Shop-Domain`/`shopify-shop-domain`. The signature check still passes because it only re-hashes the body, and `Registry.process` forwards the forged `shop` value straight into `WebhookMetadata` for the app's handler to act on.

### Impact Explanation
This crosses a tenant boundary the gem is supposed to enforce: a webhook payload legitimately produced under one merchant's HMAC secret usage can be attributed, by this library, to an arbitrary other shop domain chosen by the sender. Any application logic keyed off `WebhookMetadata#shop` (e.g., "look up shop B's record and update it with this body") can be manipulated by an attacker who only controls their own installed shop, resulting in cross-tenant data injection/corruption. This matches the Critical "cross-tenant access" impact category, since the identity binding between authenticated payload and claimed tenant is broken entirely within this gem's own verification logic.

### Likelihood Explanation
Exploitability requires only: (1) the attacker has (or creates) any shop with the target app installed so they can trigger a real, HMAC-signed webhook with attacker-influenced body content, and (2) the app's webhook endpoint is internet-reachable, which it must be for Shopify to deliver webhooks. No access to `api_secret_key`, access tokens, or the app's `client_secret` is needed — the attacker never needs to compute the HMAC themselves, only replay one that Shopify already computed for their own shop's traffic with a substituted header. This is a realistic, low-privilege internet-reachable path.

### Recommendation
Bind the tenant identity into the verified material instead of trusting an unauthenticated header:
- Include the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) values in the string that is HMAC-verified (e.g., extend `to_signable_string` to canonically include these header values, or validate them out-of-band against a separately authenticated channel), so that `Utils::HmacValidator.validate` fails if the header doesn't match the shop that actually produced the signed body.
- Alternatively/additionally, cross-check the `shop-domain` header against a known/expected shop (e.g., the shop associated with an existing session or registration) before dispatching to the handler in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and edits a field that ends up in a webhook body they can trigger (e.g., product title -> `products/update` webhook), causing Shopify to POST a body `B` with a valid `X-Shopify-Hmac-Sha256` header `H = HMAC-SHA256(secret, B)` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker captures this `(B, H)` pair (their own traffic, fully visible to them).
3. Attacker sends a new POST to the app's webhook endpoint with the identical body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(secret, B)` — unchanged since only the body is hashed — and returns `true`. `Registry.process` calls the app's handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the app to process attacker-controlled content as though it came from `victim-shop.myshopify.com`.

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
