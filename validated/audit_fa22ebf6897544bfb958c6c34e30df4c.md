### Title
Webhook HMAC only signs the raw body, not the `shop-domain` header, allowing shop-identity spoofing in `ShopifyAPI::Webhooks::Request` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using an HMAC that covers only the raw request body, while the `shop` (and `topic`) values that the host application actually acts on are read directly from HTTP headers that are never included in the signed material. This breaks the identity binding `HMAC-verified bytes == bytes acted on`, allowing a request whose body has a valid signature for the shared `client_secret` to be relabeled as belonging to a different shop.

### Finding Description
`Request#hmac` computes/exposes the signature that must be checked against the raw body: [1](#0-0) 

`Request#to_signable_string` — the bytes that are actually HMAC-verified by `Utils::HmacValidator.validate` — is defined as just the raw JSON body: [2](#0-1) 

But `Request#shop`, `Request#topic`, `Request#api_version`, and `Request#webhook_id` — the fields the host application uses to route the webhook to a handler and to decide which tenant/session the payload applies to — are pulled straight from HTTP headers that are outside the signed payload entirely: [3](#0-2) 

`HmacValidator.validate` (shared with the OAuth callback flow) only ever checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`: [4](#0-3) 

Because `to_signable_string` for a webhook is solely `@raw_body`, the `shop-domain` header can be modified in transit (or replayed with a different header while keeping the original signed body) without invalidating the HMAC check. Every shop on a Shopify plus-app instance shares the same `client_secret`, so a legitimately-received, validly-signed webhook body from Shop A can be re-submitted to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header c

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L36-38)
```ruby
      def to_signable_string
        @raw_body
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
