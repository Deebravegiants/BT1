### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, so the HMAC verification performed by `Utils::HmacValidator.validate` never covers the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. Any attacker who possesses one valid `(raw_body, hmac-sha256)` pair — e.g. from a webhook legitimately delivered to their own shop — can replay that exact body/signature while substituting an arbitrary `x-shopify-shop-domain` (and topic/webhook-id) header. `Webhooks::Registry.process` accepts the request as authentic and hands the attacker-chosen `shop` value straight to the app's handler.

### Finding Description
The gem's webhook flow is: [1](#0-0) 

`process` validates the request via `Utils::HmacValidator.validate(request)`, then builds `WebhookMetadata` using `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — none of which are checked by the HMAC.

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [3](#0-2) 

Contrast this with the OAuth callback verifier `Auth::Oauth::AuthQuery`, where the exact same `HmacValidator` is used but `to_signable_string` explicitly folds `shop` into the signed string, binding the shop identity to the signature: [4](#0-3) 

So the equality the gem is supposed to enforce is:

`shop_authenticated_by_hmac == shop_acted_on_by_handler`

For OAuth this holds (`shop` is inside the signed payload). For webhooks it does not: `request.shop` (and `topic`/`webhook_id`/`api_version`) are read straight from unauthenticated headers while the HMAC only certifies the body bytes: [5](#0-4) 

Because Shopify signs webhooks using the app's single `client_secret` for every shop that installs the app, an attacker who legitimately installs the target app on their own shop can capture a real `(body, x-shopify-hmac-sha256)` pair produced for their own shop's webhook, then send a forged HTTP request to the app's webhook endpoint reusing that exact body/HMAC but with the `x-shopify-shop-domain` header changed to a different (victim) shop domain. `HmacValidator.validate` recomputes the HMAC only over the (unchanged) body and it matches, so `Registry.process` treats the forged request as authentic and dispatches it to the handler with `shop` set to the attacker-chosen value.

### Impact Explanation
This breaks the tenant-identity binding the app relies on to attribute webhook events to the correct shop. Any downstream logic that uses `WebhookMetadata#shop` (e.g. to look up a per-shop stored session/access token, write records scoped to that shop, or gate business logic) can be made to act as though the event originated from a shop the attacker does not control. This is a cross-tenant confusion/impersonation vector rooted directly in this gem's `Webhooks::Request`/`HmacValidator` implementation, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on a shop they control (a normal, unprivileged action for any Shopify merchant), capture one legitimate webhook delivery for their own shop, and replay it with a modified header at the app's public webhook endpoint. No access token, `client_secret`, or privileged credential is needed — only network access to the app's webhook route.

### Recommendation
Include the values the application will trust and act upon — at minimum `shop-domain`, and ideally `topic`, `webhook-id`, and `api-version` — inside the string that `Webhooks::Request#to_signable_string` returns, or otherwise cryptographically bind them to the signed payload, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` folds `shop` into its signed string. Shopify's actual HMAC computation is body-only per their webhook spec, so an alternative mitigation is for the gem to explicitly document/require callers to independently validate `shop-domain` against a known-installed-shop list before trusting `WebhookMetadata#shop`, since the header is not itself authenticated by this gem.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) for their own shop.
2. Attacker captures the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent for that delivery.
3. Attacker crafts a new HTTP request to the app's webhook route, reusing the identical raw body and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. The app calls:
   ```ruby
   ShopifyAPI::Webhooks::Registry.process(
     ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
   )
   ```
   as shown in the docs' example handler.
5. `Utils::HmacValidator.validate` succeeds because it only checks `@raw_body`, per `lib/shopify_api/webhooks/request.rb:36-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`; `Registry.process` then invokes the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the request never touched Shopify with that shop context.

### Citations

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
